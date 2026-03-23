/// Cost Breakdown Widget - تفصيل التكاليف
/// Pie chart showing cost breakdown by category
library;

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/profitability_models.dart';

/// Cost Breakdown Pie Chart
class CostBreakdownWidget extends StatefulWidget {
  final Map<CostType, double> costsByType;
  final double totalCosts;
  final String locale;

  const CostBreakdownWidget({
    super.key,
    required this.costsByType,
    required this.totalCosts,
    this.locale = 'ar',
  });

  @override
  State<CostBreakdownWidget> createState() => _CostBreakdownWidgetState();
}

class _CostBreakdownWidgetState extends State<CostBreakdownWidget> {
  int touchedIndex = -1;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currencyFormat = NumberFormat('#,##0', 'ar');

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.locale == 'ar' ? 'تفصيل التكاليف' : 'Cost Breakdown',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                // Pie Chart
                Expanded(
                  flex: 2,
                  child: AspectRatio(
                    aspectRatio: 1,
                    child: PieChart(
                      PieChartData(
                        pieTouchData: PieTouchData(
                          touchCallback: (FlTouchEvent event, pieTouchResponse) {
                            setState(() {
                              if (!event.isInterestedForInteractions ||
                                  pieTouchResponse == null ||
                                  pieTouchResponse.touchedSection == null) {
                                touchedIndex = -1;
                                return;
                              }
                              touchedIndex =
                                  pieTouchResponse.touchedSection!.touchedSectionIndex;
                            });
                          },
                        ),
                        borderData: FlBorderData(show: false),
                        sectionsSpace: 2,
                        centerSpaceRadius: 40,
                        sections: _getSections(),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                // Legend
                Expanded(
                  flex: 1,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: _buildLegend(currencyFormat),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Total
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer.withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    widget.locale == 'ar' ? 'إجمالي التكاليف' : 'Total Costs',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '${currencyFormat.format(widget.totalCosts)} ${widget.locale == 'ar' ? 'ريال' : 'YER'}',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<PieChartSectionData> _getSections() {
    final colors = _getColors();
    final entries = widget.costsByType.entries.toList();

    return List.generate(entries.length, (index) {
      final isTouched = index == touchedIndex;
      final radius = isTouched ? 60.0 : 50.0;
      final fontSize = isTouched ? 16.0 : 12.0;

      final entry = entries[index];
      final percentage = (entry.value / widget.totalCosts) * 100;

      return PieChartSectionData(
        color: colors[index % colors.length],
        value: entry.value,
        title: '${percentage.toStringAsFixed(1)}%',
        radius: radius,
        titleStyle: TextStyle(
          fontSize: fontSize,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      );
    });
  }

  List<Widget> _buildLegend(NumberFormat currencyFormat) {
    final colors = _getColors();
    final entries = widget.costsByType.entries.toList();

    return List.generate(entries.length, (index) {
      final entry = entries[index];
      final percentage = (entry.value / widget.totalCosts) * 100;

      return Padding(
        padding: const EdgeInsets.only(bottom: 8.0),
        child: Row(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: colors[index % colors.length],
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    entry.key.getName(widget.locale),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    '${percentage.toStringAsFixed(1)}%',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    });
  }

  List<Color> _getColors() {
    return [
      const Color(0xFF2196F3), // Blue
      const Color(0xFF4CAF50), // Green
      const Color(0xFFFFC107), // Amber
      const Color(0xFFF44336), // Red
      const Color(0xFF9C27B0), // Purple
      const Color(0xFFFF9800), // Orange
      const Color(0xFF00BCD4), // Cyan
      const Color(0xFF795548), // Brown
      const Color(0xFF607D8B), // Blue Grey
      const Color(0xFFE91E63), // Pink
    ];
  }
}

/// Detailed Cost List Widget
class DetailedCostListWidget extends StatelessWidget {
  final List<CostCategory> costs;
  final String locale;
  final Function(CostCategory)? onTap;

  const DetailedCostListWidget({
    super.key,
    required this.costs,
    this.locale = 'ar',
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currencyFormat = NumberFormat('#,##0', 'ar');
    final dateFormat = DateFormat('yyyy-MM-dd', locale);

    // Group costs by type
    final groupedCosts = <CostType, List<CostCategory>>{};
    for (final cost in costs) {
      groupedCosts.putIfAbsent(cost.type, () => []).add(cost);
    }

    return Card(
      elevation: 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              locale == 'ar' ? 'تفاصيل التكاليف' : 'Cost Details',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const Divider(height: 1),
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: groupedCosts.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final type = groupedCosts.keys.elementAt(index);
              final typeCosts = groupedCosts[type]!;
              final totalAmount = typeCosts.fold<double>(
                0,
                (sum, cost) => sum + cost.amount,
              );

              return ExpansionTile(
                leading: _getCostIcon(type),
                title: Text(
                  type.getName(locale),
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                subtitle: Text(
                  '${currencyFormat.format(totalAmount)} ${locale == 'ar' ? 'ريال' : 'YER'}',
                  style: theme.textTheme.bodySmall,
                ),
                children: typeCosts.map((cost) {
                  return ListTile(
                    dense: true,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 72,
                      vertical: 4,
                    ),
                    title: Text(cost.getDisplayName(locale)),
                    subtitle: Text(dateFormat.format(cost.date)),
                    trailing: Text(
                      '${currencyFormat.format(cost.amount)} ${locale == 'ar' ? 'ريال' : 'YER'}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    onTap: onTap != null ? () => onTap!(cost) : null,
                  );
                }).toList(),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _getCostIcon(CostType type) {
    IconData icon;
    Color color;

    switch (type) {
      case CostType.seeds:
        icon = Icons.eco;
        color = Colors.green;
        break;
      case CostType.fertilizer:
        icon = Icons.science;
        color = Colors.blue;
        break;
      case CostType.pesticides:
        icon = Icons.pest_control;
        color = Colors.orange;
        break;
      case CostType.labor:
        icon = Icons.people;
        color = Colors.purple;
        break;
      case CostType.irrigation:
        icon = Icons.water_drop;
        color = Colors.cyan;
        break;
      case CostType.equipment:
        icon = Icons.agriculture;
        color = Colors.brown;
        break;
      case CostType.land:
        icon = Icons.landscape;
        color = Colors.teal;
        break;
      case CostType.transport:
        icon = Icons.local_shipping;
        color = Colors.indigo;
        break;
      case CostType.storage:
        icon = Icons.warehouse;
        color = Colors.deepOrange;
        break;
      case CostType.other:
        icon = Icons.more_horiz;
        color = Colors.grey;
        break;
    }

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(icon, color: color, size: 24),
    );
  }
}
