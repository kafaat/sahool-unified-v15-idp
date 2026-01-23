import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

/// Switch Settings Tile Widget
/// عنصر إعدادات مع مفتاح تشغيل/إيقاف
class SwitchSettingsTile extends StatelessWidget {
  /// Title text
  final String title;

  /// Arabic title (takes priority in RTL layout)
  final String titleAr;

  /// Optional subtitle
  final String? subtitle;

  /// Dynamic subtitle based on switch value
  final String Function(bool value)? dynamicSubtitle;

  /// Leading icon
  final IconData icon;

  /// Icon background color
  final Color? iconColor;

  /// Current switch value
  final bool value;

  /// Callback when switch is toggled
  final ValueChanged<bool>? onChanged;

  /// Whether the tile is enabled
  final bool enabled;

  /// Active color for the switch
  final Color? activeColor;

  const SwitchSettingsTile({
    super.key,
    required this.title,
    required this.titleAr,
    required this.icon,
    required this.value,
    this.subtitle,
    this.dynamicSubtitle,
    this.iconColor,
    this.onChanged,
    this.enabled = true,
    this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveIconColor = iconColor ?? SahoolTheme.primary;
    final effectiveActiveColor = activeColor ?? SahoolTheme.primary;
    final displaySubtitle = dynamicSubtitle?.call(value) ?? subtitle;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: enabled ? () => onChanged?.call(!value) : null,
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
                    color: effectiveIconColor.withOpacity(isDark ? 0.2 : 0.1),
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
                      if (displaySubtitle != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          displaySubtitle,
                          style: TextStyle(
                            fontSize: 13,
                            color: isDark ? Colors.grey[400] : Colors.grey[600],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

                // Switch
                Switch.adaptive(
                  value: value,
                  onChanged: enabled ? onChanged : null,
                  activeColor: effectiveActiveColor,
                  activeTrackColor: effectiveActiveColor.withOpacity(0.5),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Switch Settings Tile with description
/// عنصر إعدادات مع مفتاح ووصف مفصل
class DescriptiveSwitchTile extends StatelessWidget {
  final String titleAr;
  final String description;
  final IconData icon;
  final Color? iconColor;
  final bool value;
  final ValueChanged<bool>? onChanged;
  final bool enabled;

  const DescriptiveSwitchTile({
    super.key,
    required this.titleAr,
    required this.description,
    required this.icon,
    required this.value,
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
      child: InkWell(
        onTap: enabled ? () => onChanged?.call(!value) : null,
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
                        color: effectiveIconColor.withOpacity(isDark ? 0.2 : 0.1),
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
                      child: Text(
                        titleAr,
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w500,
                          color: isDark ? Colors.white : Colors.black87,
                        ),
                      ),
                    ),
                    Switch.adaptive(
                      value: value,
                      onChanged: enabled ? onChanged : null,
                      activeColor: effectiveIconColor,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Padding(
                  padding: const EdgeInsets.only(right: 52),
                  child: Text(
                    description,
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark ? Colors.grey[400] : Colors.grey[600],
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
