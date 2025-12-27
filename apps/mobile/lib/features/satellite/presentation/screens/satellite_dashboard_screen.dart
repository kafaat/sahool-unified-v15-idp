/// Satellite Dashboard Screen - شاشة لوحة الأقمار الصناعية
/// Main dashboard for satellite monitoring features
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/satellite_provider.dart';
import '../../widgets/health_indicator.dart';
import '../../widgets/weather_card.dart';
import '../../widgets/ndvi_chart.dart';
import 'ndvi_detail_screen.dart';
import 'weather_screen.dart';
import 'phenology_screen.dart';

class SatelliteDashboardScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String fieldName;

  const SatelliteDashboardScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  ConsumerState<SatelliteDashboardScreen> createState() => _SatelliteDashboardScreenState();
}

class _SatelliteDashboardScreenState extends ConsumerState<SatelliteDashboardScreen> {
  @override
  void initState() {
    super.initState();
    // Load dashboard data on init
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(satelliteDashboardProvider.notifier).loadDashboard(widget.fieldId);
    });
  }

  Future<void> _refreshDashboard() async {
    await ref.read(satelliteDashboardProvider.notifier).refreshDashboard(widget.fieldId);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(satelliteDashboardProvider);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text(
          isArabic ? 'مراقبة الأقمار الصناعية' : 'Satellite Monitoring',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF367C2B), // SAHOOL green
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: state.isLoading ? null : _refreshDashboard,
            tooltip: isArabic ? 'تحديث' : 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () => _showOptionsMenu(context, isArabic),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshDashboard,
        color: const Color(0xFF367C2B),
        child: state.isLoading && !state.hasData
            ? _buildLoadingState(isArabic)
            : state.error != null && !state.hasData
                ? _buildErrorState(state.error!, isArabic)
                : _buildDashboardContent(context, state, isArabic),
      ),
    );
  }

  Widget _buildLoadingState(bool isArabic) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
          ),
          const SizedBox(height: 16),
          Text(
            isArabic ? 'جاري تحميل بيانات الأقمار الصناعية...' : 'Loading satellite data...',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error, bool isArabic) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.satellite_alt, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshDashboard,
              icon: const Icon(Icons.refresh),
              label: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardContent(BuildContext context, SatelliteDashboardState state, bool isArabic) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Field header
        _buildFieldHeader(isArabic),
        const SizedBox(height: 16),

        // Health Score Card
        if (state.fieldHealth != null)
          _buildHealthScoreCard(state.fieldHealth!, context, isArabic),
        const SizedBox(height: 16),

        // NDVI Card
        if (state.ndviAnalysis != null)
          _buildNdviCard(state.ndviAnalysis!, context, isArabic),
        const SizedBox(height: 16),

        // Weather Card
        if (state.weatherSummary != null)
          WeatherCard(
            weather: state.weatherSummary!,
            onTap: () => _navigateToWeather(context),
          ),
        const SizedBox(height: 16),

        // Growth Stage Card
        if (state.phenologyData != null)
          _buildGrowthStageCard(state.phenologyData!, context, isArabic),
        const SizedBox(height: 16),

        // Alerts Section
        if (state.fieldHealth?.alerts.isNotEmpty ?? false)
          _buildAlertsSection(state.fieldHealth!.alerts, isArabic),
        const SizedBox(height: 16),

        // Recommendations Section
        if (state.fieldHealth?.recommendations.isNotEmpty ?? false)
          _buildRecommendationsSection(state.fieldHealth!.recommendations, isArabic),

        // Last update info
        if (state.lastUpdate != null) _buildLastUpdateInfo(state.lastUpdate!, isArabic),
      ],
    );
  }

  Widget _buildFieldHeader(bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF367C2B).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.landscape,
              color: Color(0xFF367C2B),
              size: 28,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.fieldName,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  isArabic ? 'المراقبة بالأقمار الصناعية' : 'Satellite Monitoring',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthScoreCard(dynamic fieldHealth, BuildContext context, bool isArabic) {
    return GestureDetector(
      onTap: () {
        // Show health details dialog
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Text(
              isArabic ? 'صحة الحقل' : 'Field Health',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            HealthIndicator(
              score: fieldHealth.healthScore,
              status: fieldHealth.status.value,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNdviCard(dynamic ndviAnalysis, BuildContext context, bool isArabic) {
    return GestureDetector(
      onTap: () => _navigateToNdviDetail(context),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isArabic ? 'مؤشر NDVI' : 'NDVI Index',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Icon(Icons.arrow_forward_ios, size: 16),
              ],
            ),
            const SizedBox(height: 16),
            if (ndviAnalysis.timeSeries.isNotEmpty)
              SizedBox(
                height: 120,
                child: NdviChart(
                  data: ndviAnalysis.timeSeries,
                  currentValue: ndviAnalysis.currentNdvi,
                ),
              ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNdviStat(
                  isArabic ? 'الحالي' : 'Current',
                  ndviAnalysis.currentNdvi.toStringAsFixed(2),
                  isArabic,
                ),
                _buildNdviStat(
                  isArabic ? 'التغيير' : 'Change',
                  '${ndviAnalysis.changeRate >= 0 ? '+' : ''}${ndviAnalysis.changeRate.toStringAsFixed(1)}%',
                  isArabic,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNdviStat(String label, String value, bool isArabic) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF367C2B),
          ),
        ),
      ],
    );
  }

  Widget _buildGrowthStageCard(dynamic phenologyData, BuildContext context, bool isArabic) {
    return GestureDetector(
      onTap: () => _navigateToPhenology(context),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isArabic ? 'مرحلة النمو' : 'Growth Stage',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Icon(Icons.arrow_forward_ios, size: 16),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              phenologyData.currentStage.getLabel(isArabic),
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF367C2B),
              ),
            ),
            const SizedBox(height: 8),
            if (phenologyData.daysToHarvest != null)
              Text(
                isArabic
                    ? 'باقي ${phenologyData.daysToHarvest} يوم للحصاد'
                    : '${phenologyData.daysToHarvest} days to harvest',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertsSection(List<dynamic> alerts, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning, color: Colors.red[700]),
              const SizedBox(width: 8),
              Text(
                isArabic ? 'تنبيهات' : 'Alerts',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.red[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...alerts.take(3).map((alert) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  '• ${isArabic ? alert.messageAr : alert.message}',
                  style: TextStyle(color: Colors.red[900]),
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildRecommendationsSection(List<dynamic> recommendations, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb, color: Colors.blue[700]),
              const SizedBox(width: 8),
              Text(
                isArabic ? 'توصيات' : 'Recommendations',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...recommendations.take(3).map((rec) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  '• ${isArabic ? rec.titleAr : rec.title}',
                  style: TextStyle(color: Colors.blue[900]),
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildLastUpdateInfo(DateTime lastUpdate, bool isArabic) {
    final timeAgo = DateTime.now().difference(lastUpdate);
    String timeText;

    if (timeAgo.inMinutes < 60) {
      timeText = isArabic ? 'منذ ${timeAgo.inMinutes} دقيقة' : '${timeAgo.inMinutes} minutes ago';
    } else if (timeAgo.inHours < 24) {
      timeText = isArabic ? 'منذ ${timeAgo.inHours} ساعة' : '${timeAgo.inHours} hours ago';
    } else {
      timeText = isArabic ? 'منذ ${timeAgo.inDays} يوم' : '${timeAgo.inDays} days ago';
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Center(
        child: Text(
          '${isArabic ? 'آخر تحديث' : 'Last updated'}: $timeText',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  void _navigateToNdviDetail(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => NdviDetailScreen(
          fieldId: widget.fieldId,
          fieldName: widget.fieldName,
        ),
      ),
    );
  }

  void _navigateToWeather(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => WeatherScreen(
          fieldId: widget.fieldId,
          fieldName: widget.fieldName,
        ),
      ),
    );
  }

  void _navigateToPhenology(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PhenologyScreen(
          fieldId: widget.fieldId,
          fieldName: widget.fieldName,
        ),
      ),
    );
  }

  void _showOptionsMenu(BuildContext context, bool isArabic) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.download),
              title: Text(isArabic ? 'تصدير البيانات' : 'Export Data'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Implement export
              },
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: Text(isArabic ? 'عرض السجل' : 'View History'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Implement history
              },
            ),
          ],
        ),
      ),
    );
  }
}
