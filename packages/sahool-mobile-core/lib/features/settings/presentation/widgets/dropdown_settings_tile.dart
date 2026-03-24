import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

/// Dropdown option model
/// نموذج خيار القائمة المنسدلة
class DropdownOption<T> {
  final T value;
  final String label;
  final String labelAr;
  final IconData? icon;

  const DropdownOption({
    required this.value,
    required this.label,
    required this.labelAr,
    this.icon,
  });
}

/// Dropdown Settings Tile Widget
/// عنصر إعدادات مع قائمة منسدلة
class DropdownSettingsTile<T> extends StatelessWidget {
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

  /// Current selected value
  final T value;

  /// List of available options
  final List<DropdownOption<T>> options;

  /// Callback when value changes
  final ValueChanged<T?>? onChanged;

  /// Whether the tile is enabled
  final bool enabled;

  /// Use bottom sheet instead of dropdown
  final bool useBottomSheet;

  const DropdownSettingsTile({
    super.key,
    required this.title,
    required this.titleAr,
    required this.icon,
    required this.value,
    required this.options,
    this.subtitle,
    this.iconColor,
    this.onChanged,
    this.enabled = true,
    this.useBottomSheet = true,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveIconColor = iconColor ?? SahoolTheme.primary;
    final selectedOption = options.firstWhere(
      (o) => o.value == value,
      orElse: () => options.first,
    );

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: enabled
            ? () {
                if (useBottomSheet) {
                  _showBottomSheet(context, selectedOption);
                }
              }
            : null,
        child: Opacity(
          opacity: enabled ? 1.0 : 0.5,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                // Icon container
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

                // Title and subtitle
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

                // Selected value display
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      selectedOption.labelAr,
                      style: TextStyle(
                        fontSize: 14,
                        color: isDark ? Colors.grey[400] : Colors.grey[600],
                      ),
                    ),
                    const SizedBox(width: 4),
                    Icon(
                      Icons.chevron_left_rounded,
                      color: isDark ? Colors.grey[600] : Colors.grey[400],
                      size: 24,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showBottomSheet(BuildContext context, DropdownOption<T> selectedOption) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => _DropdownBottomSheet<T>(
        titleAr: titleAr,
        options: options,
        selectedValue: value,
        onSelected: (selected) {
          Navigator.pop(context);
          onChanged?.call(selected);
        },
      ),
    );
  }
}

/// Bottom sheet for dropdown selection
class _DropdownBottomSheet<T> extends StatelessWidget {
  final String titleAr;
  final List<DropdownOption<T>> options;
  final T selectedValue;
  final ValueChanged<T> onSelected;

  const _DropdownBottomSheet({
    required this.titleAr,
    required this.options,
    required this.selectedValue,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: isDark ? Colors.grey[900] : Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle
          Container(
            margin: const EdgeInsets.only(top: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[400],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          // Title
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              titleAr,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const Divider(height: 1),
          // Options
          ...options.map((option) => _buildOption(context, option)),
          SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
        ],
      ),
    );
  }

  Widget _buildOption(BuildContext context, DropdownOption<T> option) {
    final isSelected = option.value == selectedValue;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => onSelected(option.value),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          color: isSelected
              ? SahoolTheme.primary.withValues(alpha: isDark ? 0.2 : 0.05)
              : null,
          child: Row(
            children: [
              if (option.icon != null) ...[
                Icon(
                  option.icon,
                  color: isSelected ? SahoolTheme.primary : Colors.grey,
                  size: 22,
                ),
                const SizedBox(width: 12),
              ],
              Expanded(
                child: Text(
                  option.labelAr,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    color: isSelected
                        ? SahoolTheme.primary
                        : (isDark ? Colors.white : Colors.black87),
                  ),
                ),
              ),
              if (isSelected)
                const Icon(
                  Icons.check_circle,
                  color: SahoolTheme.primary,
                  size: 22,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Radio Group Settings Tile (inline options)
/// عنصر إعدادات مع مجموعة خيارات راديو
class RadioGroupSettingsTile<T> extends StatelessWidget {
  final String titleAr;
  final IconData icon;
  final Color? iconColor;
  final T value;
  final List<DropdownOption<T>> options;
  final ValueChanged<T?>? onChanged;
  final bool enabled;

  const RadioGroupSettingsTile({
    super.key,
    required this.titleAr,
    required this.icon,
    required this.value,
    required this.options,
    this.iconColor,
    this.onChanged,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveIconColor = iconColor ?? SahoolTheme.primary;

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
                  Text(
                    titleAr,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                      color: isDark ? Colors.white : Colors.black87,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // Radio options
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: options.map((option) {
                  final isSelected = option.value == value;
                  return ChoiceChip(
                    label: Text(option.labelAr),
                    selected: isSelected,
                    onSelected: enabled ? (_) => onChanged?.call(option.value) : null,
                    selectedColor: effectiveIconColor.withValues(alpha: 0.2),
                    checkmarkColor: effectiveIconColor,
                    labelStyle: TextStyle(
                      color: isSelected ? effectiveIconColor : null,
                      fontWeight: isSelected ? FontWeight.bold : null,
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
