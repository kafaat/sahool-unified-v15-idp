/// NDVI Detail Screen - شاشة تفاصيل NDVI
/// Detailed view of NDVI time series and vegetation indices
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/satellite_provider.dart';
import '../../widgets/ndvi_chart.dart';

class NdviDetailScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String fieldName;

  const NdviDetailScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  ConsumerState<NdviDetailScreen> createState() => _NdviDetailScreenState();
}

class _NdviDetailScreenState extends ConsumerState<NdviDetailScreen> {
  int _selectedDays = 30;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(ndviDetailProvider.notifier).loadNdviDetails(widget.fieldId, days: _selectedDays);
    });
  }

  Future<void> _refreshData() async {
    await ref.read(ndviDetailProvider.notifier).refreshNdviDetails(widget.fieldId, days: _selectedDays);
  }

  void _changePeriod(int days) {
    setState(() => _selectedDays = days);
    ref.read(ndviDetailProvider.notifier).loadNdviDetails(widget.fieldId, days: days);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(ndviDetailProvider);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text(
          isArabic ? 'تفاصيل NDVI' : 'NDVI Details',
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
            ? const Center(child: CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF367C2B))))
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
            Icon(Icons.error_outline, size: 64, color: Colors.grey[400]),
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

  Widget _buildContent(dynamic state, bool isArabic) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Period selector
        _buildPeriodSelector(isArabic),
        const SizedBox(height: 16),

        // NDVI Chart
        if (state.timeSeries.isNotEmpty) _buildChartCard(state, isArabic),
        const SizedBox(height: 16),

        // Current values
        if (state.analysis != null) _buildCurrentValues(state.analysis, isArabic),
        const SizedBox(height: 16),

        // Vegetation Indices Grid
        if (state.indices.isNotEmpty) _buildIndicesGrid(state.indices, isArabic),
        const SizedBox(height: 16),

        // Health Status & Recommendations
        if (state.analysis != null) _buildHealthStatus(state.analysis, isArabic),
      ],
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
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildPeriodButton(7, isArabic ? '7 أيام' : '7 Days', isArabic),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _buildPeriodButton(30, isArabic ? '30 يوم' : '30 Days', isArabic),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _buildPeriodButton(90, isArabic ? '90 يوم' : '90 Days', isArabic),
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
          ),
        ),
      ),
    );
  }

  Widget _buildChartCard(dynamic state, bool isArabic) {
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'السلسلة الزمنية لـ NDVI' : 'NDVI Time Series',
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

  Widget _buildCurrentValues(dynamic analysis, bool isArabic) {
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'القيم الحالية' : 'Current Values',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildValueCard(
                  isArabic ? 'NDVI الحالي' : 'Current NDVI',
                  analysis.currentNdvi.toStringAsFixed(2),
                  Colors.green,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildValueCard(
                  isArabic ? 'التغيير' : 'Change',
                  '${analysis.changeRate >= 0 ? '+' : ''}${analysis.changeRate.toStringAsFixed(1)}%',
                  analysis.changeRate >= 0 ? Colors.green : Colors.red,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildValueCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIndicesGrid(Map<String, double> indices, bool isArabic) {
    final indicesList = indices.entries.toList();

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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'المؤشرات النباتية' : 'Vegetation Indices',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 1.5,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: indicesList.length,
            itemBuilder: (context, index) {
              final entry = indicesList[index];
              return _buildIndexCard(entry.key, entry.value);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildIndexCard(String name, double value) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF367C2B).withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF367C2B).withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            name.toUpperCase(),
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Color(0xFF367C2B),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value.toStringAsFixed(2),
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthStatus(dynamic analysis, bool isArabic) {
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'حالة الصحة' : 'Health Status',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            analysis.health.getLabel(isArabic),
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF367C2B),
            ),
          ),
        ],
      ),
    );
  }
}
