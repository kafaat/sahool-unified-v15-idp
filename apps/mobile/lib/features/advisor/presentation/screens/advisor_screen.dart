/// Advisor Screen - Agricultural Advisory Dashboard
/// شاشة المستشار - لوحة الاستشارات الزراعية
///
/// Full advisory screen with:
/// - Today's recommendations cards (irrigation, fertilizer, pest)
/// - Priority-sorted actions list
/// - Field selector
/// - Weather-based suggestions
/// - Economic analysis card (cost/ROI)
/// - Arabic/English bilingual
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/advisor_provider.dart';
import '../widgets/recommendation_card.dart';
import '../../../ai_advisor/presentation/screens/ai_advisor_screen.dart';

/// Full agricultural advisor dashboard screen
/// شاشة لوحة المستشار الزراعي الكاملة
class AdvisorDashboardScreen extends ConsumerWidget {
  const AdvisorDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final advisorState = ref.watch(advisorDashboardProvider);

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: _buildAppBar(context, ref, advisorState),
      body: advisorState.isLoading
          ? const Center(
              child:
                  CircularProgressIndicator(color: SahoolColors.forestGreen),
            )
          : advisorState.error != null
              ? _buildErrorState(ref, advisorState.error!)
              : RefreshIndicator(
                  onRefresh: () => ref
                      .read(advisorDashboardProvider.notifier)
                      .loadRecommendations(),
                  color: SahoolColors.forestGreen,
                  child: _buildBody(context, ref, advisorState),
                ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openAIChat(context),
        backgroundColor: SahoolColors.forestGreen,
        icon: const Icon(Icons.psychology, color: Colors.white),
        label: const Text(
          'Ask AI | اسال الذكاء الاصطناعي',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(
      BuildContext context, WidgetRef ref, AdvisorDashboardState state) {
    return AppBar(
      title: const Text('Farm Advisor | المستشار الزراعي'),
      backgroundColor: Colors.white,
      foregroundColor: SahoolColors.forestGreen,
      elevation: 0,
      actions: [
        // Urgent count badge
        if (state.urgentRecommendations.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(left: 8),
            child: Center(
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: SahoolColors.danger,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${state.urgentRecommendations.length} Urgent | عاجل',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        IconButton(
          icon: const Icon(Icons.refresh),
          onPressed: () => ref
              .read(advisorDashboardProvider.notifier)
              .loadRecommendations(),
          tooltip: 'Refresh | تحديث',
        ),
      ],
    );
  }

  Widget _buildErrorState(WidgetRef ref, String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline,
              size: 48, color: SahoolColors.danger),
          const SizedBox(height: 16),
          Text(
            'Error loading recommendations\nخطا في تحميل التوصيات',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref
                .read(advisorDashboardProvider.notifier)
                .loadRecommendations(),
            child: const Text('Retry | اعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(
      BuildContext context, WidgetRef ref, AdvisorDashboardState state) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Weather summary card
        _buildWeatherCard(context),
        const SizedBox(height: 16),

        // Field selector
        _buildFieldSelector(ref, state),
        const SizedBox(height: 16),

        // Summary statistics
        _buildSummaryRow(state),
        const SizedBox(height: 20),

        // Economic overview
        _buildEconomicOverview(state),
        const SizedBox(height: 20),

        // Priority actions section title
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Today\'s Actions | اجراءات اليوم',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: SahoolColors.forestGreen,
              ),
            ),
            Text(
              '${state.filteredRecommendations.where((r) => !r.isCompleted).length} pending | معلقة',
              style: TextStyle(fontSize: 12, color: Colors.grey[500]),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Recommendation cards
        ...state.filteredRecommendations.map((rec) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: RecommendationCard(
                recommendation: rec,
                onAction: () {},
                onComplete: () => ref
                    .read(advisorDashboardProvider.notifier)
                    .markCompleted(rec.id),
              ),
            )),

        const SizedBox(height: 80), // Space for FAB
      ],
    );
  }

  // ===========================================================================
  // Weather Card
  // بطاقة الطقس
  // ===========================================================================

  Widget _buildWeatherCard(BuildContext context) {
    return OrganicCard(
      color: SahoolColors.forestGreen,
      isPrimary: true,
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Weather Today | طقس اليوم',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    '28 C - Sunny | مشمس',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Humidity: 45% | Wind: 12 km/h NW',
                    style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.8), fontSize: 12),
                  ),
                ],
              ),
              const Icon(Icons.wb_sunny, color: Colors.amber, size: 52),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.warning_amber,
                    color: Colors.amber, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Frost warning tomorrow night (2 C) | تحذير صقيع الليلة القادمة',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.9),
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // Field Selector
  // محدد الحقل
  // ===========================================================================

  Widget _buildFieldSelector(WidgetRef ref, AdvisorDashboardState state) {
    final fields = [
      ('all', 'All Fields | كل الحقول'),
      ('field_1', 'Field 1 | الحقل 1'),
      ('field_2', 'Field 2 | الحقل 2'),
      ('field_3', 'Field 3 | الحقل 3'),
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: fields.map((field) {
          final isSelected =
              (state.selectedFieldId ?? 'all') == field.$1;
          return Padding(
            padding: const EdgeInsets.only(left: 8),
            child: GestureDetector(
              onTap: () => ref
                  .read(advisorDashboardProvider.notifier)
                  .selectField(field.$1),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected
                      ? SahoolColors.forestGreen
                      : Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isSelected
                        ? SahoolColors.forestGreen
                        : Colors.grey.withValues(alpha: 0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.location_on,
                      size: 14,
                      color:
                          isSelected ? Colors.white : Colors.grey,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      field.$2,
                      style: TextStyle(
                        color: isSelected
                            ? Colors.white
                            : Colors.grey[700],
                        fontWeight: isSelected
                            ? FontWeight.bold
                            : FontWeight.normal,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ===========================================================================
  // Summary Statistics
  // احصائيات الملخص
  // ===========================================================================

  Widget _buildSummaryRow(AdvisorDashboardState state) {
    final irrigationCount = state.recommendations
        .where((r) => r.type == RecommendationType.irrigation)
        .length;
    final fertilizerCount = state.recommendations
        .where((r) => r.type == RecommendationType.fertilizer)
        .length;
    final pestCount = state.recommendations
        .where((r) =>
            r.type == RecommendationType.pest ||
            r.type == RecommendationType.disease)
        .length;
    final completedCount =
        state.recommendations.where((r) => r.isCompleted).length;

    return Row(
      children: [
        Expanded(
          child: _SummaryBadge(
            icon: Icons.water_drop,
            count: irrigationCount,
            label: 'Irrigation | ري',
            color: SahoolColors.info,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _SummaryBadge(
            icon: Icons.science,
            count: fertilizerCount,
            label: 'Fertilizer | تسميد',
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _SummaryBadge(
            icon: Icons.bug_report,
            count: pestCount,
            label: 'Pest | آفات',
            color: const Color(0xFFFF8F00),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _SummaryBadge(
            icon: Icons.check_circle,
            count: completedCount,
            label: 'Done | تم',
            color: SahoolColors.sageGreen,
          ),
        ),
      ],
    );
  }

  // ===========================================================================
  // Economic Overview
  // نظرة عامة اقتصادية
  // ===========================================================================

  Widget _buildEconomicOverview(AdvisorDashboardState state) {
    final totalCost = state.recommendations.fold<double>(
        0.0, (sum, r) => sum + (r.estimatedCost ?? 0));
    final totalROI = state.recommendations.fold<double>(
        0.0, (sum, r) => sum + (r.estimatedROI ?? 0));
    final netBenefit = totalROI - totalCost;

    return OrganicCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.analytics, color: SahoolColors.harvestGold, size: 20),
              SizedBox(width: 8),
              Text(
                'Economic Analysis | التحليل الاقتصادي',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _EconomicStat(
                  label: 'Total Cost | التكلفة',
                  value: '${totalCost.toStringAsFixed(0)} SAR',
                  color: SahoolColors.danger,
                ),
              ),
              Container(
                width: 1,
                height: 40,
                color: Colors.grey[200],
              ),
              Expanded(
                child: _EconomicStat(
                  label: 'Expected Return | العائد',
                  value: '${totalROI.toStringAsFixed(0)} SAR',
                  color: SahoolColors.success,
                ),
              ),
              Container(
                width: 1,
                height: 40,
                color: Colors.grey[200],
              ),
              Expanded(
                child: _EconomicStat(
                  label: 'Net Benefit | الصافي',
                  value: '${netBenefit.toStringAsFixed(0)} SAR',
                  color: SahoolColors.forestGreen,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // ROI bar
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: totalROI > 0
                  ? (netBenefit / totalROI).clamp(0.0, 1.0)
                  : 0.0,
              backgroundColor: SahoolColors.danger.withValues(alpha: 0.2),
              valueColor: const AlwaysStoppedAnimation<Color>(
                  SahoolColors.success),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            totalCost > 0 && totalROI > 0
                ? 'ROI: ${((totalROI / totalCost) * 100).toStringAsFixed(0)}% | Invest to grow | استثمر لتنمو'
                : 'No investments needed | لا توجد استثمارات مطلوبة',
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[500],
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // AI Chat Navigation
  // التنقل لمحادثة الذكاء الاصطناعي
  // ===========================================================================

  void _openAIChat(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
            'Opening AI Advisor... | جاري فتح المستشار الذكي...'),
        behavior: SnackBarBehavior.floating,
      ),
    );
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const AiAdvisorScreen(),
      ),
    );
  }
}

// =============================================================================
// Helper Widgets
// عناصر مساعدة
// =============================================================================

class _SummaryBadge extends StatelessWidget {
  final IconData icon;
  final int count;
  final String label;
  final Color color;

  const _SummaryBadge({
    required this.icon,
    required this.count,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Column(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 4),
          Text(
            '$count',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 9, color: Colors.grey[500]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _EconomicStat extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _EconomicStat({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(fontSize: 10, color: Colors.grey[500]),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
