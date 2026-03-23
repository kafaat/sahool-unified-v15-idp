/// Irrigation Method Selector Widget - أداة اختيار طريقة الري
/// Dropdown/card selector for irrigation methods with efficiency display
/// and icons for drip, sprinkler, flood, pivot.
/// أداة اختيار طرق الري مع عرض الكفاءة وأيقونات لكل طريقة
library;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../data/remote/irrigation_api.dart';

/// Callback when an irrigation method is selected
typedef OnMethodSelected = void Function(IrrigationMethod method);

/// Irrigation Method Selector - Card-based selector
/// أداة اختيار طريقة الري بنمط البطاقات
class IrrigationMethodSelector extends StatefulWidget {
  final List<IrrigationMethod> methods;
  final String? selectedMethodId;
  final OnMethodSelected? onMethodSelected;
  final bool isArabic;
  final bool showEfficiency;
  final bool isCompact;

  const IrrigationMethodSelector({
    super.key,
    required this.methods,
    this.selectedMethodId,
    this.onMethodSelected,
    this.isArabic = true,
    this.showEfficiency = true,
    this.isCompact = false,
  });

  @override
  State<IrrigationMethodSelector> createState() =>
      _IrrigationMethodSelectorState();
}

class _IrrigationMethodSelectorState extends State<IrrigationMethodSelector> {
  String? _selectedId;

  @override
  void initState() {
    super.initState();
    _selectedId = widget.selectedMethodId;
  }

  @override
  void didUpdateWidget(IrrigationMethodSelector oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.selectedMethodId != oldWidget.selectedMethodId) {
      _selectedId = widget.selectedMethodId;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.methods.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.water, size: 48, color: Colors.grey[300]),
              const SizedBox(height: 12),
              Text(
                widget.isArabic
                    ? 'لا توجد طرق ري متاحة'
                    : 'No irrigation methods available',
                style: TextStyle(color: Colors.grey[500]),
              ),
            ],
          ),
        ),
      );
    }

    if (widget.isCompact) {
      return _buildCompactSelector();
    }

    return _buildCardSelector();
  }

  /// Full card-based selector with icons and efficiency bars
  Widget _buildCardSelector() {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: widget.methods.length,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final method = widget.methods[index];
        final isSelected = _selectedId == method.id;

        return _MethodCard(
          method: method,
          isSelected: isSelected,
          isArabic: widget.isArabic,
          showEfficiency: widget.showEfficiency,
          onTap: () {
            setState(() => _selectedId = method.id);
            widget.onMethodSelected?.call(method);
          },
        );
      },
    );
  }

  /// Compact horizontal chip selector
  Widget _buildCompactSelector() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: widget.methods.map((method) {
          final isSelected = _selectedId == method.id;
          final icon = _getMethodIcon(method.id);
          final color = _getMethodColor(method.id);

          return Padding(
            padding: const EdgeInsets.only(right: 10),
            child: GestureDetector(
              onTap: () {
                setState(() => _selectedId = method.id);
                widget.onMethodSelected?.call(method);
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? color : Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isSelected ? color : Colors.grey.withOpacity(0.3),
                    width: isSelected ? 2 : 1,
                  ),
                  boxShadow: isSelected
                      ? [
                          BoxShadow(
                            color: color.withOpacity(0.2),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ]
                      : null,
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      icon,
                      size: 18,
                      color: isSelected ? Colors.white : color,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      widget.isArabic ? method.nameAr : method.nameEn,
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.grey[700],
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
                        fontSize: 13,
                      ),
                    ),
                    if (widget.showEfficiency) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? Colors.white.withOpacity(0.2)
                              : color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '${(method.efficiency * 100).toInt()}%',
                          style: TextStyle(
                            fontSize: 10,
                            color: isSelected ? Colors.white : color,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Method Card Widget
// ═══════════════════════════════════════════════════════════════════════════════

class _MethodCard extends StatelessWidget {
  final IrrigationMethod method;
  final bool isSelected;
  final bool isArabic;
  final bool showEfficiency;
  final VoidCallback onTap;

  const _MethodCard({
    required this.method,
    required this.isSelected,
    required this.isArabic,
    required this.showEfficiency,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final icon = _getMethodIcon(method.id);
    final color = _getMethodColor(method.id);
    final efficiencyPercent = (method.efficiency * 100).toInt();

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.08) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? color : Colors.grey.withOpacity(0.15),
            width: isSelected ? 2 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: color.withOpacity(0.15),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.05),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
        ),
        child: Row(
          children: [
            // Method icon
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: isSelected
                    ? color.withOpacity(0.15)
                    : color.withOpacity(0.08),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                icon,
                color: color,
                size: 28,
              ),
            ),
            const SizedBox(width: 14),

            // Method info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isArabic ? method.nameAr : method.nameEn,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: isSelected ? color : Colors.black87,
                    ),
                  ),
                  if (method.description.isNotEmpty)
                    Text(
                      method.description,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  if (showEfficiency) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        // Efficiency bar
                        Expanded(
                          child: Stack(
                            children: [
                              Container(
                                height: 6,
                                decoration: BoxDecoration(
                                  color: Colors.grey[200],
                                  borderRadius: BorderRadius.circular(3),
                                ),
                              ),
                              FractionallySizedBox(
                                widthFactor: method.efficiency.clamp(0, 1),
                                child: Container(
                                  height: 6,
                                  decoration: BoxDecoration(
                                    color: _getEfficiencyColor(
                                        efficiencyPercent),
                                    borderRadius: BorderRadius.circular(3),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '$efficiencyPercent%',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: _getEfficiencyColor(efficiencyPercent),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      isArabic
                          ? 'كفاءة الري: ${_getEfficiencyLabel(efficiencyPercent)}'
                          : 'Efficiency: ${_getEfficiencyLabelEn(efficiencyPercent)}',
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[500],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Selection indicator
            if (isSelected)
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.check,
                  color: Colors.white,
                  size: 18,
                ),
              )
            else
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey[300]!),
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Color _getEfficiencyColor(int percent) {
    if (percent >= 90) return SahoolColors.forestGreen;
    if (percent >= 75) return Colors.green;
    if (percent >= 60) return SahoolColors.harvestGold;
    if (percent >= 40) return Colors.orange;
    return SahoolColors.danger;
  }

  String _getEfficiencyLabel(int percent) {
    if (percent >= 90) return 'ممتازة';
    if (percent >= 75) return 'جيدة';
    if (percent >= 60) return 'متوسطة';
    if (percent >= 40) return 'منخفضة';
    return 'ضعيفة';
  }

  String _getEfficiencyLabelEn(int percent) {
    if (percent >= 90) return 'Excellent';
    if (percent >= 75) return 'Good';
    if (percent >= 60) return 'Moderate';
    if (percent >= 40) return 'Low';
    return 'Poor';
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Dropdown-based Method Selector (for forms)
// ═══════════════════════════════════════════════════════════════════════════════

/// Dropdown irrigation method selector for forms
/// قائمة منسدلة لاختيار طريقة الري في النماذج
class IrrigationMethodDropdown extends StatelessWidget {
  final List<IrrigationMethod> methods;
  final String? selectedMethodId;
  final ValueChanged<String?> onChanged;
  final bool isArabic;

  const IrrigationMethodDropdown({
    super.key,
    required this.methods,
    this.selectedMethodId,
    required this.onChanged,
    this.isArabic = true,
  });

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      value: selectedMethodId,
      decoration: InputDecoration(
        labelText: isArabic ? 'طريقة الري' : 'Irrigation Method',
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        prefixIcon: const Icon(Icons.water, color: SahoolColors.forestGreen),
        filled: true,
        fillColor: Colors.grey[50],
      ),
      isExpanded: true,
      items: methods.map((method) {
        final icon = _getMethodIcon(method.id);
        final color = _getMethodColor(method.id);
        final effPercent = (method.efficiency * 100).toInt();

        return DropdownMenuItem<String>(
          value: method.id,
          child: Row(
            children: [
              Icon(icon, color: color, size: 22),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  isArabic ? method.nameAr : method.nameEn,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: _getEfficiencyBarColor(effPercent).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '$effPercent%',
                  style: TextStyle(
                    fontSize: 11,
                    color: _getEfficiencyBarColor(effPercent),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
      onChanged: onChanged,
    );
  }

  Color _getEfficiencyBarColor(int percent) {
    if (percent >= 90) return SahoolColors.forestGreen;
    if (percent >= 75) return Colors.green;
    if (percent >= 60) return SahoolColors.harvestGold;
    return Colors.orange;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Method Icon Helper - أيقونات طرق الري
// ═══════════════════════════════════════════════════════════════════════════════

/// Get icon for irrigation method based on its ID
IconData _getMethodIcon(String methodId) {
  final id = methodId.toLowerCase();
  if (id.contains('drip') || id.contains('trickle') || id.contains('تنقيط')) {
    return Icons.opacity;
  }
  if (id.contains('sprinkler') || id.contains('رش')) {
    return Icons.shower;
  }
  if (id.contains('pivot') || id.contains('محوري')) {
    return Icons.rotate_right;
  }
  if (id.contains('flood') || id.contains('surface') || id.contains('غمر')) {
    return Icons.waves;
  }
  if (id.contains('furrow') || id.contains('أخدود')) {
    return Icons.terrain;
  }
  if (id.contains('micro') || id.contains('مجهري')) {
    return Icons.blur_on;
  }
  if (id.contains('sub') || id.contains('تحت')) {
    return Icons.layers;
  }
  // Default water icon
  return Icons.water;
}

/// Get color for irrigation method based on its ID
Color _getMethodColor(String methodId) {
  final id = methodId.toLowerCase();
  if (id.contains('drip') || id.contains('trickle') || id.contains('تنقيط')) {
    return SahoolColors.forestGreen;
  }
  if (id.contains('sprinkler') || id.contains('رش')) {
    return Colors.blue;
  }
  if (id.contains('pivot') || id.contains('محوري')) {
    return Colors.indigo;
  }
  if (id.contains('flood') || id.contains('surface') || id.contains('غمر')) {
    return Colors.teal;
  }
  if (id.contains('furrow') || id.contains('أخدود')) {
    return SahoolColors.earthBrown;
  }
  if (id.contains('micro') || id.contains('مجهري')) {
    return Colors.purple;
  }
  if (id.contains('sub') || id.contains('تحت')) {
    return Colors.brown;
  }
  return SahoolColors.sageGreen;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Method Comparison Widget
// ═══════════════════════════════════════════════════════════════════════════════

/// Shows a visual comparison of irrigation methods
/// عرض مقارنة مرئية لطرق الري
class IrrigationMethodComparison extends StatelessWidget {
  final List<IrrigationMethod> methods;
  final bool isArabic;

  const IrrigationMethodComparison({
    super.key,
    required this.methods,
    this.isArabic = true,
  });

  @override
  Widget build(BuildContext context) {
    // Sort methods by efficiency
    final sorted = List<IrrigationMethod>.from(methods)
      ..sort((a, b) => b.efficiency.compareTo(a.efficiency));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isArabic ? 'مقارنة طرق الري' : 'Irrigation Method Comparison',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 16),
        ...sorted.map((method) {
          final icon = _getMethodIcon(method.id);
          final color = _getMethodColor(method.id);
          final effPercent = (method.efficiency * 100).toInt();

          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              children: [
                Icon(icon, color: color, size: 22),
                const SizedBox(width: 10),
                SizedBox(
                  width: 80,
                  child: Text(
                    isArabic ? method.nameAr : method.nameEn,
                    style: const TextStyle(fontSize: 13),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Stack(
                    children: [
                      Container(
                        height: 20,
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      FractionallySizedBox(
                        widthFactor: method.efficiency.clamp(0, 1),
                        child: Container(
                          height: 20,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                color.withOpacity(0.6),
                                color,
                              ],
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          alignment: Alignment.centerRight,
                          padding: const EdgeInsets.only(right: 8),
                          child: Text(
                            '$effPercent%',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
        const SizedBox(height: 8),
        Text(
          isArabic
              ? 'الكفاءة العالية تعني استهلاك أقل للمياه'
              : 'Higher efficiency means less water consumption',
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[500],
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
}
