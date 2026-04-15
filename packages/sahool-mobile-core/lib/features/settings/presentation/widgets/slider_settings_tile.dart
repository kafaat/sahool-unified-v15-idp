import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

/// Slider Settings Tile Widget
/// عنصر إعدادات مع شريط تمرير
class SliderSettingsTile extends StatelessWidget {
  /// Title text
  final String title;

  /// Arabic title (takes priority in RTL layout)
  final String titleAr;

  /// Optional subtitle
  final String? subtitle;

  /// Leading icon
  final IconData icon;

  /// Icon background color
  final Color? iconColor;

  /// Current slider value
  final double value;

  /// Minimum value
  final double min;

  /// Maximum value
  final double max;

  /// Number of divisions
  final int? divisions;

  /// Callback when slider value changes
  final ValueChanged<double>? onChanged;

  /// Callback when slider is done changing
  final ValueChanged<double>? onChangeEnd;

  /// Whether the tile is enabled
  final bool enabled;

  /// Label formatter for displaying current value
  final String Function(double)? labelFormatter;

  /// Show min/max labels
  final bool showMinMaxLabels;

  /// Min label
  final String? minLabel;

  /// Max label
  final String? maxLabel;

  const SliderSettingsTile({
    super.key,
    required this.title,
    required this.titleAr,
    required this.icon,
    required this.value,
    this.subtitle,
    this.iconColor,
    this.min = 0.0,
    this.max = 100.0,
    this.divisions,
    this.onChanged,
    this.onChangeEnd,
    this.enabled = true,
    this.labelFormatter,
    this.showMinMaxLabels = false,
    this.minLabel,
    this.maxLabel,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveIconColor = iconColor ?? SahoolTheme.primary;
    final displayValue = labelFormatter?.call(value) ?? value.toStringAsFixed(0);

    return Material(
      color: Colors.transparent,
      child: Opacity(
        opacity: enabled ? 1.0 : 0.5,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: effectiveIconColor.withValues(alpha: isDark ? 0.2 : 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      icon,
                      color: effectiveIconColor,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          titleAr,
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            color: isDark ? Colors.white : Colors.black87,
                          ),
                        ),
                        if (subtitle != null) ...[
                          const SizedBox(height: 2),
                          Text(
                            subtitle!,
                            style: TextStyle(
                              fontSize: 13,
                              color: isDark ? Colors.grey[400] : Colors.grey[600],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  // Current value display
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: effectiveIconColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      displayValue,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: effectiveIconColor,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Slider
              SliderTheme(
                data: SliderTheme.of(context).copyWith(
                  activeTrackColor: effectiveIconColor,
                  inactiveTrackColor: effectiveIconColor.withValues(alpha: 0.2),
                  thumbColor: effectiveIconColor,
                  overlayColor: effectiveIconColor.withValues(alpha: 0.1),
                  trackHeight: 4,
                  thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
                ),
                child: Slider(
                  value: value,
                  min: min,
                  max: max,
                  divisions: divisions,
                  onChanged: enabled ? onChanged : null,
                  onChangeEnd: enabled ? onChangeEnd : null,
                ),
              ),

              // Min/Max labels
              if (showMinMaxLabels)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        minLabel ?? min.toStringAsFixed(0),
                        style: TextStyle(
                          fontSize: 12,
                          color: isDark ? Colors.grey[500] : Colors.grey[600],
                        ),
                      ),
                      Text(
                        maxLabel ?? max.toStringAsFixed(0),
                        style: TextStyle(
                          fontSize: 12,
                          color: isDark ? Colors.grey[500] : Colors.grey[600],
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
}

/// Range Slider Settings Tile
/// عنصر إعدادات مع شريط نطاق
class RangeSliderSettingsTile extends StatelessWidget {
  final String titleAr;
  final String? subtitle;
  final IconData icon;
  final Color? iconColor;
  final RangeValues values;
  final double min;
  final double max;
  final int? divisions;
  final ValueChanged<RangeValues>? onChanged;
  final bool enabled;
  final String Function(double)? labelFormatter;

  const RangeSliderSettingsTile({
    super.key,
    required this.titleAr,
    required this.icon,
    required this.values,
    this.subtitle,
    this.iconColor,
    this.min = 0.0,
    this.max = 100.0,
    this.divisions,
    this.onChanged,
    this.enabled = true,
    this.labelFormatter,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveIconColor = iconColor ?? SahoolTheme.primary;
    final startLabel = labelFormatter?.call(values.start) ?? values.start.toStringAsFixed(0);
    final endLabel = labelFormatter?.call(values.end) ?? values.end.toStringAsFixed(0);

    return Material(
      color: Colors.transparent,
      child: Opacity(
        opacity: enabled ? 1.0 : 0.5,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: effectiveIconColor.withValues(alpha: isDark ? 0.2 : 0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      icon,
                      color: effectiveIconColor,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          titleAr,
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            color: isDark ? Colors.white : Colors.black87,
                          ),
                        ),
                        if (subtitle != null)
                          Text(
                            subtitle!,
                            style: TextStyle(
                              fontSize: 13,
                              color: isDark ? Colors.grey[400] : Colors.grey[600],
                            ),
                          ),
                      ],
                    ),
                  ),
                  Text(
                    '$startLabel - $endLabel',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: effectiveIconColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SliderTheme(
                data: SliderTheme.of(context).copyWith(
                  activeTrackColor: effectiveIconColor,
                  inactiveTrackColor: effectiveIconColor.withValues(alpha: 0.2),
                  thumbColor: effectiveIconColor,
                  overlayColor: effectiveIconColor.withValues(alpha: 0.1),
                ),
                child: RangeSlider(
                  values: values,
                  min: min,
                  max: max,
                  divisions: divisions,
                  onChanged: enabled ? onChanged : null,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
