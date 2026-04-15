library;

/// Satellite History Screen - شاشة سجل الأقمار الصناعية
/// Displays historical satellite analyses for a field

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/satellite_provider.dart';
import '../../widgets/ndvi_chart.dart';

class SatelliteHistoryScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String fieldName;

  const SatelliteHistoryScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  ConsumerState<SatelliteHistoryScreen> createState() =>
      _SatelliteHistoryScreenState();
}

class _SatelliteHistoryScreenState
    extends ConsumerState<SatelliteHistoryScreen> {
  int _selectedDays = 90;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref
          .read(ndviDetailProvider.notifier)
          .loadNdviDetails(widget.fieldId, days: _selectedDays);
    });
  }

  Future<void> _refreshData() async {
    await ref
        .read(ndviDetailProvider.notifier)
        .refreshNdviDetails(widget.fieldId, days: _selectedDays);
  }

  void _changePeriod(int days) {
    setState(() => _selectedDays = days);
    ref
        .read(ndviDetailProvider.notifier)
        .loadNdviDetails(widget.fieldId, days: days);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(ndviDetailProvider);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text(
          isArabic ? 'سجل التحليلات' : 'Analysis History',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF367C2B),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: _refreshData,
        color: const Color(0xFF367C2B),
        child: state.isLoading
            ? const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
                ),
              )
            : state.error != null
                ? _buildErrorState(state.error!, isArabic)
                : _buildContent(state, isArabic),
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
            Icon(Icons.history, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(error, textAlign: TextAlign.center),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshData,
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

  Widget _buildContent(NdviDetailState state, bool isArabic) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Field name header
        _buildFieldHeader(isArabic),
        const SizedBox(height: 16),

        // Period selector
        _buildPeriodSelector(isArabic),
        const SizedBox(height: 16),

        // Historical NDVI Chart
        if (state.timeSeries.isNotEmpty) _buildHistoryChart(state, isArabic),
        const SizedBox(height: 16),

        // Historical data points list
        if (state.timeSeries.isNotEmpty) _buildHistoryList(state, isArabic),
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
            color: Colors.black.withValues(alpha: 0.05),
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
              color: const Color(0xFF367C2B).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.history,
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
                  isArabic
                      ? 'سجل التحليلات التاريخية'
                      : 'Historical Analysis Records',
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

  Widget _buildPeriodSelector(bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildPeriodButton(
                30, isArabic ? '30 يوم' : '30 Days', isArabic),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _buildPeriodButton(
                90, isArabic ? '90 يوم' : '90 Days', isArabic),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _buildPeriodButton(
                180, isArabic ? '180 يوم' : '180 Days', isArabic),
          ),
          const SizedBox(width: 8),
          Expanded(
            child:
                _buildPeriodButton(365, isArabic ? 'سنة' : '1 Year', isArabic),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodButton(int days, String label, bool isArabic) {
    final isSelected = _selectedDays == days;
    return GestureDetector(
      onTap: () => _changePeriod(days),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF367C2B) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.grey[700],
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            fontSize: 12,
          ),
        ),
      ),
    );
  }

  Widget _buildHistoryChart(NdviDetailState state, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'تاريخ NDVI' : 'NDVI History',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: NdviChart(
              data: state.timeSeries,
              currentValue: state.analysis?.currentNdvi ?? 0.0,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryList(NdviDetailState state, bool isArabic) {
    // Sort by date descending (most recent first)
    final sortedData = List.of(state.timeSeries)
      ..sort((a, b) => b.date.compareTo(a.date));

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
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
                isArabic ? 'سجل القراءات' : 'Reading Records',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                '${sortedData.length} ${isArabic ? 'قراءة' : 'readings'}',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: sortedData.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final dataPoint = sortedData[index];
              return _buildHistoryItem(dataPoint, isArabic);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryItem(dynamic dataPoint, bool isArabic) {
    final date = dataPoint.date;
    final ndvi = dataPoint.ndvi;

    // Determine health status based on NDVI value
    final (String status, Color color) = _getNdviStatus(ndvi, isArabic);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          // Date
          Expanded(
            flex: 2,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _formatDate(date, isArabic),
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  _formatTime(date),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
          // NDVI Value
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              ndvi.toStringAsFixed(2),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Status
          Expanded(
            flex: 1,
            child: Text(
              status,
              style: TextStyle(
                fontSize: 12,
                color: color,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }

  (String, Color) _getNdviStatus(double ndvi, bool isArabic) {
    if (ndvi >= 0.7) {
      return (isArabic ? 'ممتاز' : 'Excellent', Colors.green[700]!);
    } else if (ndvi >= 0.5) {
      return (isArabic ? 'جيد' : 'Good', Colors.green[500]!);
    } else if (ndvi >= 0.3) {
      return (isArabic ? 'متوسط' : 'Moderate', Colors.orange[600]!);
    } else if (ndvi >= 0.1) {
      return (isArabic ? 'ضعيف' : 'Poor', Colors.orange[800]!);
    } else {
      return (isArabic ? 'حرج' : 'Critical', Colors.red[700]!);
    }
  }

  String _formatDate(DateTime date, bool isArabic) {
    final months = isArabic
        ? [
            'يناير',
            'فبراير',
            'مارس',
            'أبريل',
            'مايو',
            'يونيو',
            'يوليو',
            'أغسطس',
            'سبتمبر',
            'أكتوبر',
            'نوفمبر',
            'ديسمبر'
          ]
        : [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec'
          ];

    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }

  String _formatTime(DateTime date) {
    final hour = date.hour.toString().padLeft(2, '0');
    final minute = date.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
