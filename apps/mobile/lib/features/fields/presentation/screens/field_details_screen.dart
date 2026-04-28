import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';
import '../../../../core/di/providers.dart';
import '../../../../core/widgets/field_context_header.dart';
import '../../domain/entities/field_entity.dart';
import '../../../weather/presentation/providers/weather_provider.dart';

/// شاشة تفاصيل الحقل
/// Field Details Screen
class FieldDetailsScreen extends ConsumerStatefulWidget {
  final FieldEntity field;

  const FieldDetailsScreen({super.key, required this.field});

  @override
  ConsumerState<FieldDetailsScreen> createState() => _FieldDetailsScreenState();
}

class _FieldDetailsScreenState extends ConsumerState<FieldDetailsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    // Trigger weather load for this specific field
    Future.microtask(() {
      if (mounted) {
        ref.read(weatherProvider.notifier).loadWeather(widget.field.id);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) => [
            _buildSliverAppBar(),
          ],
          body: TabBarView(
            controller: _tabController,
            children: [
              _buildOverviewTab(),
              _buildHealthTab(),
              _buildTasksTab(),
              _buildHistoryTab(),
            ],
          ),
        ),
        floatingActionButton: _buildSpeedDial(),
      ),
    );
  }

  Widget _buildSliverAppBar() {
    return SliverAppBar(
      expandedHeight: 280,
      pinned: true,
      backgroundColor: const Color(0xFF367C2B),
      foregroundColor: Colors.white,
      flexibleSpace: FlexibleSpaceBar(
        background: DecoratedBox(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 60, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Field header
                  Row(
                    children: [
                      Container(
                        width: 70,
                        height: 70,
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Center(
                          child: Text(
                            widget.field.cropEmoji,
                            style: const TextStyle(fontSize: 40),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.field.name,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withValues(alpha: 0.2),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    widget.field.cropType,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: _getStatusColor(widget.field.status)
                                        .withValues(alpha: 0.3),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    widget.field.status.arabicLabel,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Quick stats
                  Row(
                    children: [
                      _buildQuickStat(
                        icon: Icons.square_foot,
                        value: widget.field.areaHectares.toStringAsFixed(1),
                        label: 'هكتار',
                      ),
                      const SizedBox(width: 24),
                      _buildQuickStat(
                        icon: Icons.grass,
                        value: widget.field.ndviValue?.toStringAsFixed(2) ?? '-',
                        label: 'NDVI',
                      ),
                      const SizedBox(width: 24),
                      _buildQuickStat(
                        icon: Icons.favorite,
                        value: '${(widget.field.healthScore * 100).round()}%',
                        label: 'الصحة',
                      ),
                      const SizedBox(width: 24),
                      _buildQuickStat(
                        icon: Icons.water_drop,
                        value: widget.field.ndwiValue?.toStringAsFixed(2) ?? '-',
                        label: 'NDWI',
                      ),
                    ],
                  ),

                  const SizedBox(height: 10),

                  // Data provenance timestamp
                  Row(
                    children: [
                      const Icon(Icons.update, color: Colors.white70, size: 12),
                      const SizedBox(width: 4),
                      Text(
                        'آخر تحديث: ${_formatTimestamp(widget.field.updatedAt)}',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
      bottom: TabBar(
        controller: _tabController,
        indicatorColor: Colors.white,
        labelColor: Colors.white,
        unselectedLabelColor: Colors.white70,
        tabs: const [
          Tab(text: 'نظرة عامة', icon: Icon(Icons.dashboard, size: 20)),
          Tab(text: 'الصحة', icon: Icon(Icons.eco, size: 20)),
          Tab(text: 'المهام', icon: Icon(Icons.task, size: 20)),
          Tab(text: 'السجل', icon: Icon(Icons.history, size: 20)),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.map),
          onPressed: () => _openMap(),
          tooltip: 'الخريطة',
        ),
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert),
          onSelected: _handleMenuAction,
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'edit', child: Text('تعديل')),
            const PopupMenuItem(value: 'share', child: Text('مشاركة')),
            const PopupMenuItem(value: 'export', child: Text('تصدير')),
            const PopupMenuItem(
              value: 'delete',
              child: Text('حذف', style: TextStyle(color: Colors.red)),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickStat({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Column(
      children: [
        Icon(icon, color: Colors.white.withValues(alpha: 0.8), size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.7),
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Field context banner (data provenance – who/what/when)
          FieldContextHeader(field: widget.field),
          const SizedBox(height: 20),

          // Info cards
          _buildSectionTitle('معلومات الحقل'),
          _buildInfoCard(),

          const SizedBox(height: 24),

          // Growth progress
          if (widget.field.plantingDate != null) ...[
            _buildSectionTitle('تقدم النمو'),
            _buildGrowthProgressCard(),
            const SizedBox(height: 24),
          ],

          // Weather summary
          _buildSectionTitle('ملخص الطقس'),
          _buildWeatherCard(),

          const SizedBox(height: 24),

          // Recent activity
          _buildSectionTitle('النشاط الأخير'),
          _buildRecentActivity(),

          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Color(0xFF367C2B),
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildInfoRow(Icons.landscape, 'نوع التربة', widget.field.soilType ?? 'غير محدد'),
            const Divider(),
            _buildInfoRow(Icons.water_drop, 'نظام الري', widget.field.irrigationType ?? 'غير محدد'),
            if (widget.field.lastIrrigation != null) ...[
              const Divider(),
              _buildInfoRow(
                Icons.schedule,
                'آخر ري',
                _formatDate(widget.field.lastIrrigation!),
              ),
            ],
            if (widget.field.plantingDate != null) ...[
              const Divider(),
              _buildInfoRow(
                Icons.eco,
                'تاريخ الزراعة',
                _formatDate(widget.field.plantingDate!),
              ),
            ],
            if (widget.field.expectedHarvest != null) ...[
              const Divider(),
              _buildInfoRow(
                Icons.agriculture,
                'موعد الحصاد المتوقع',
                _formatDate(widget.field.expectedHarvest!),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF367C2B), size: 22),
          const SizedBox(width: 12),
          Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildGrowthProgressCard() {
    final daysSincePlanting = widget.field.daysSincePlanting ?? 0;
    final daysUntilHarvest = widget.field.daysUntilHarvest ?? 0;
    final totalDays = daysSincePlanting + daysUntilHarvest;
    final progress = totalDays > 0 ? daysSincePlanting / totalDays : 0.0;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('منذ الزراعة'),
                    Text(
                      '$daysSincePlanting يوم',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                        color: Color(0xFF367C2B),
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text('حتى الحصاد'),
                    Text(
                      '$daysUntilHarvest يوم',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                        color: Colors.orange,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey[200],
                valueColor: const AlwaysStoppedAnimation(Color(0xFF367C2B)),
                minHeight: 12,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${(progress * 100).round()}% من دورة النمو',
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherCard() {
    final weatherState = ref.watch(weatherProvider);

    final String temp;
    final String condition;
    final String humidity;
    final String wind;

    if (weatherState.isLoading) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    } else if (weatherState.data != null) {
      final current = weatherState.data!.current;
      temp = '${current.temperature.round()}°C';
      condition = current.conditionAr;
      humidity = '${current.humidity}%';
      wind = '${current.windSpeed.toStringAsFixed(0)} كم/س';
    } else {
      temp = '—';
      condition = 'لا توجد بيانات طقس';
      humidity = '—';
      wind = '—';
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.wb_sunny, color: Colors.orange, size: 48),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    temp,
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    condition,
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Row(
                  children: [
                    const Icon(Icons.water_drop, size: 16, color: Colors.blue),
                    const SizedBox(width: 4),
                    Text(humidity, style: TextStyle(color: Colors.grey[600])),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.air, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(wind, style: TextStyle(color: Colors.grey[600])),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.history, size: 40, color: Colors.grey[300]),
            const SizedBox(height: 12),
            Text(
              'لا توجد أنشطة مسجلة',
              style: TextStyle(
                fontSize: 15,
                color: Colors.grey[500],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'ستظهر هنا آخر العمليات بعد مزامنة البيانات',
              style: TextStyle(color: Colors.grey[400], fontSize: 12),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityItem({
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
    required String time,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text(subtitle),
      trailing: Text(
        time,
        style: TextStyle(color: Colors.grey[500], fontSize: 12),
      ),
    );
  }

  Widget _buildHealthTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Health score card
          _buildHealthScoreCard(),
          const SizedBox(height: 24),

          // Indices
          _buildSectionTitle('المؤشرات'),
          _buildIndicesCard(),
          const SizedBox(height: 24),

          // Recommendations
          _buildSectionTitle('التوصيات'),
          _buildRecommendationsCard(),

          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Widget _buildHealthScoreCard() {
    final healthColor = _getHealthColor(widget.field.healthScore);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            SizedBox(
              width: 150,
              height: 150,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 150,
                    height: 150,
                    child: CircularProgressIndicator(
                      value: widget.field.healthScore,
                      strokeWidth: 12,
                      backgroundColor: Colors.grey[200],
                      valueColor: AlwaysStoppedAnimation(healthColor),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${(widget.field.healthScore * 100).round()}%',
                        style: TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: healthColor,
                        ),
                      ),
                      Text(
                        widget.field.healthLabel,
                        style: TextStyle(
                          color: healthColor,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIndicesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildIndexRow('NDVI', widget.field.ndviValue, Colors.green),
            const Divider(),
            _buildIndexRow('NDWI', widget.field.ndwiValue, Colors.blue),
            const Divider(),
            // NDRE is not yet available in FieldEntity (requires Sentinel-2 red-edge
            // band processing). Displayed as '—' until the data pipeline is wired.
            _buildIndexRow('NDRE', null, Colors.orange),
          ],
        ),
      ),
    );
  }

  Widget _buildIndexRow(String name, double? value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text(
            name,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(width: 8),
          if (value != null)
            Text(
              _indexInterpretation(name, value),
              style: TextStyle(fontSize: 11, color: color.withValues(alpha: 0.8)),
            ),
          const Spacer(),
          if (value != null) ...[
            SizedBox(
              width: 120,
              child: LinearProgressIndicator(
                value: (value + 1) / 2, // Normalize -1 to 1 range
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation(color),
                minHeight: 8,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const SizedBox(width: 12),
            Text(
              value.toStringAsFixed(2),
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ] else
            Text('—', style: TextStyle(color: Colors.grey[400], fontSize: 14)),
        ],
      ),
    );
  }

  /// Returns a short agronomic interpretation for an index value.
  /// يُعيد تفسيراً زراعياً مختصراً لقيمة المؤشر.
  String _indexInterpretation(String name, double value) {
    switch (name) {
      case 'NDVI':
        if (value >= 0.6) return '· نمو ممتاز';
        if (value >= 0.4) return '· نمو جيد';
        if (value >= 0.2) return '· نمو ضعيف';
        return '· يحتاج تدخلاً';
      case 'NDWI':
        if (value >= 0.3) return '· مستوى مائي كافٍ';
        if (value >= 0.15) return '· مراقبة الري';
        return '· يحتاج ريّاً';
      default:
        return '';
    }
  }

  /// Formats a DateTime as a short Arabic date+time string.
  String _formatTimestamp(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    if (diff.inDays == 1) return 'البارحة';
    if (diff.inDays < 7) return 'منذ ${diff.inDays} أيام';
    return '${dt.day}/${dt.month}/${dt.year}';
  }

  Widget _buildRecommendationsCard() {
    final recs = _deriveRecommendations();

    if (recs.isEmpty) {
      return Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
          child: Center(
            child: Column(
              children: [
                Icon(Icons.check_circle_outline, color: Colors.green[400], size: 40),
                const SizedBox(height: 8),
                Text(
                  'الحقل في حالة جيدة – لا توجد توصيات فورية',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          for (int i = 0; i < recs.length; i++) ...[
            if (i > 0) const Divider(height: 1),
            _buildRecommendationItem(
              icon: recs[i].icon,
              color: recs[i].color,
              title: recs[i].title,
              description: recs[i].description,
              priority: recs[i].priority,
            ),
          ],
        ],
      ),
    );
  }

  /// Derives recommendations from live NDVI / NDWI / health values with
  /// multi-index correlation and an honest confidence disclaimer when trend
  /// data is unavailable (snapshot-only context).
  ///
  /// Nitrogen fertilizer is only recommended when soil moisture is comfortably
  /// above this threshold. Below it the NDVI drop may be caused by drought,
  /// pests, or phenological stage rather than nitrogen deficiency.
  static const double _nitrogenMoistureGate = 0.3;

  /// يستخرج التوصيات بربط مؤشرات متعددة مع إشارة واضحة بأن البيانات لحظية.
  List<_FieldRecommendation> _deriveRecommendations() {
    final recs = <_FieldRecommendation>[];
    final ndvi = widget.field.ndviValue;
    final ndwi = widget.field.ndwiValue;
    final health = widget.field.healthScore;

    // ── متعدد المؤشرات: إجهاد مائي + NDVI منخفض ──────────────────────────
    // كلا المؤشرين يشيران معاً لأولوية الري على التسميد
    final bool waterStress = ndwi != null && ndwi < 0.2;
    final bool lowNdvi = ndvi != null && ndvi < 0.4;
    // Extract non-nullable locals so interpolations below are safe without '!'.
    final String ndwiStr = ndwi?.toStringAsFixed(2) ?? '-';
    final String ndviStr = ndvi?.toStringAsFixed(2) ?? '-';

    if (waterStress && lowNdvi) {
      recs.add(_FieldRecommendation(
        icon: Icons.water_drop,
        color: Colors.blue,
        title: 'أولوية الري (NDWI + NDVI منخفضان)',
        description: 'كلا المؤشرين يؤكدان إجهاداً مائياً. الري أولاً قبل التسميد'
            '\n(NDWI: $ndwiStr | NDVI: $ndviStr)',
        priority: 'عاجل',
        priorityColor: Colors.red,
      ));
    } else if (waterStress) {
      recs.add(_FieldRecommendation(
        icon: Icons.water_drop,
        color: Colors.blue,
        title: 'زيادة الري',
        description: 'قيمة NDWI ($ndwiStr) منخفضة — إجهاد مائي محتمل.'
            '\nيُنصح بزيادة معدل الري.',
        priority: 'عاجل',
        priorityColor: Colors.red,
      ));
    } else if (ndwi != null && ndwi < 0.35) {
      recs.add(_FieldRecommendation(
        icon: Icons.water_drop,
        color: Colors.blueAccent,
        title: 'مراقبة الري',
        description: 'قيمة NDWI ($ndwiStr) في الحد الأدنى.'
            '\nراقب رطوبة التربة خلال 48 ساعة.',
        priority: 'متوسط',
        priorityColor: Colors.orange,
      ));
    }

    // ── NDVI بمفرده (مع غياب إجهاد مائي) → نقص نيتروجين ─────────────────
    // النيتروجين يُوصى به فقط عندما يكون الإجهاد المائي مستبعداً بشكل معقول
    // (NDWI > 0.3) لأن NDVI المنخفض قد يعكس أيضاً آفات أو أمراضاً أو مرحلة
    // نمو — وليس نقص نيتروجين بالضرورة.
    //
    // Gate: !waterStress (ndwi >= 0.2) AND ndwi > _nitrogenMoistureGate (comfortable moisture)
    // so we only suggest nitrogen when water is clearly not the limiting factor.
    final bool moistureOk = ndwi == null || ndwi > _nitrogenMoistureGate;
    if (!waterStress && moistureOk) {
      if (ndvi != null && ndvi < 0.35) {
        recs.add(_FieldRecommendation(
          icon: Icons.eco,
          color: Colors.green,
          title: 'تسميد نيتروجيني',
          description: 'قيمة NDVI (${ndvi.toStringAsFixed(2)}) منخفضة دون إجهاد مائي.'
              '\nيُشير إلى نقص كلوروفيل — يُنصح بجرعة نيتروجين.',
          priority: 'مهم',
          priorityColor: Colors.deepOrange,
        ));
      } else if (ndvi != null && ndvi < 0.5) {
        recs.add(_FieldRecommendation(
          icon: Icons.eco,
          color: Colors.lightGreen,
          title: 'متابعة النمو',
          description: 'قيمة NDVI (${ndvi.toStringAsFixed(2)}) متوسطة.'
              '\nاستمر في برنامج التسميد الحالي وراقب التحسن.',
          priority: 'منخفض',
          priorityColor: Colors.green,
        ));
      }
    } else if (!waterStress && !moistureOk) {
      // NDWI is between 0.2 and 0.3 — moisture is borderline; NDVI is also
      // low. Ambiguous stress: recommend field scouting before acting.
      if (ndvi != null && ndvi < 0.4) {
        recs.add(_FieldRecommendation(
          icon: Icons.search,
          color: Colors.amber,
          title: 'معاينة ميدانية مطلوبة',
          description: 'NDVI (${ndvi.toStringAsFixed(2)}) منخفض و NDWI ($ndwiStr) على الحد.'
              '\nالسبب غير محدد — قد يكون آفات أو مرض أو نقص تغذية. معاينة أولاً.',
          priority: 'مهم',
          priorityColor: Colors.amber.shade800,
        ));
      }
    }

    // ── مؤشر الصحة العام ──────────────────────────────────────────────────
    if (health < 0.4) {
      recs.add(_FieldRecommendation(
        icon: Icons.warning_amber,
        color: Colors.red,
        title: 'صحة الحقل منخفضة',
        description: 'مؤشر الصحة العام (${(health * 100).round()}%) ضعيف.'
            '\nيُنصح بمعاينة ميدانية فورية لتحديد السبب.',
        priority: 'عاجل',
        priorityColor: Colors.red,
      ));
    }

    // ── إشعار صدق: بيانات لحظية بدون سياق زمني ───────────────────────────
    recs.add(const _FieldRecommendation(
      icon: Icons.info_outline,
      color: Colors.blueGrey,
      title: 'ملاحظة: قراءة لحظية',
      description: 'هذه التوصيات مبنية على آخر قياس متاح فقط.\n'
          'لتحليل الاتجاه الزمني (↑/↓) افتح "صحة المحاصيل" واختر فترة أسبوع أو شهر.',
      priority: 'معلومة',
      priorityColor: Colors.blueGrey,
    ));

    return recs;
  }

  Widget _buildRecommendationItem({
    required IconData icon,
    required Color color,
    required String title,
    required String description,
    required String priority,
    Color priorityColor = Colors.orange,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text(description, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: priorityColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          priority,
          style: TextStyle(fontSize: 10, color: priorityColor),
        ),
      ),
    );
  }

  Widget _buildTasksTab() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.task_alt, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            'لا توجد مهام حالياً',
            style: TextStyle(fontSize: 18, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pushNamed(
                context,
                '/task-create',
                arguments: {'fieldId': widget.field.id, 'fieldName': widget.field.name},
              );
            },
            icon: const Icon(Icons.add),
            label: const Text('إضافة مهمة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF367C2B),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryTab() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 64, color: Colors.grey[300]),
            const SizedBox(height: 16),
            Text(
              'لا يوجد سجل نشاط',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'سيظهر هنا سجل كامل بعمليات الحقل بعد مزامنة البيانات من الخادم',
              style: TextStyle(color: Colors.grey[400], fontSize: 13),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpeedDial() {
    return FloatingActionButton.extended(
      onPressed: () => _showQuickActions(),
      backgroundColor: const Color(0xFF367C2B),
      icon: const Icon(Icons.flash_on),
      label: const Text('إجراء سريع'),
    );
  }

  void _showQuickActions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  'إجراءات سريعة',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.blue,
                  child: Icon(Icons.water_drop, color: Colors.white),
                ),
                title: const Text('تسجيل ري'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.green,
                  child: Icon(Icons.eco, color: Colors.white),
                ),
                title: const Text('تسجيل تسميد'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.orange,
                  child: Icon(Icons.camera_alt, color: Colors.white),
                ),
                title: const Text('التقاط صورة'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.purple,
                  child: Icon(Icons.note_add, color: Colors.white),
                ),
                title: const Text('إضافة ملاحظة'),
                onTap: () => Navigator.pop(context),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _openMap() {
    Navigator.pushNamed(context, '/map', arguments: {'fieldId': widget.field.id});
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'edit':
        context.push(
          '/field-form',
          extra: {'fieldId': widget.field.id},
        );
        break;
      case 'share':
        _shareField();
        break;
      case 'export':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تصدير البيانات - قريباً')),
        );
        break;
      case 'delete':
        _showDeleteConfirmation();
        break;
    }
  }

  void _shareField() {
    final field = widget.field;
    final shareText = StringBuffer()
      ..writeln('${field.name} - سهول')
      ..writeln('المحصول: ${field.cropType}')
      ..writeln('المساحة: ${field.areaHectares.toStringAsFixed(1)} هكتار')
      ..writeln('الحالة: ${field.status.arabicLabel}');
    if (field.ndviValue != null) {
      shareText.writeln('NDVI: ${field.ndviValue!.toStringAsFixed(2)}');
    }
    Share.share(shareText.toString(), subject: field.name);
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('حذف الحقل'),
        content: Text('هل أنت متأكد من حذف "${widget.field.name}"؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(dialogContext);
              try {
                final repo = ref.read(fieldsRepoProvider);
                await repo.deleteField(widget.field.id);
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم حذف الحقل بنجاح'),
                    backgroundColor: Color(0xFF367C2B),
                  ),
                );
                Navigator.pop(context, 'deleted');
              } catch (e) {
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('فشل حذف الحقل: $e'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }

  Color _getHealthColor(double score) {
    if (score >= 0.8) return const Color(0xFF2E7D32);
    if (score >= 0.6) return const Color(0xFF4CAF50);
    if (score >= 0.4) return Colors.orange;
    return Colors.red;
  }

  Color _getStatusColor(FieldStatus status) {
    switch (status) {
      case FieldStatus.active:
        return Colors.green;
      case FieldStatus.fallow:
        return Colors.grey;
      case FieldStatus.preparing:
        return Colors.blue;
      case FieldStatus.harvested:
        return Colors.orange;
      case FieldStatus.inactive:
        return Colors.red;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

/// Internal value-object for a data-derived agronomic recommendation.
/// كائن داخلي يمثل توصية زراعية مستخرجة من البيانات الحقيقية.
class _FieldRecommendation {
  final IconData icon;
  final Color color;
  final String title;
  final String description;
  final String priority;
  final Color priorityColor;

  const _FieldRecommendation({
    required this.icon,
    required this.color,
    required this.title,
    required this.description,
    required this.priority,
    required this.priorityColor,
  });
}
