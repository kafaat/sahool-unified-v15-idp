import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

/// Base Settings Tile Widget
/// عنصر الإعدادات الأساسي
class SettingsTile extends StatelessWidget {
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

  /// Trailing widget (defaults to chevron)
  final Widget? trailing;

  /// Tap callback
  final VoidCallback? onTap;

  /// Long press callback
  final VoidCallback? onLongPress;

  /// Whether the tile is enabled
  final bool enabled;

  /// Whether to show navigation arrow
  final bool showArrow;

  /// Badge count (optional)
  final int? badge;

  const SettingsTile({
    super.key,
    required this.title,
    required this.titleAr,
    required this.icon,
    this.subtitle,
    this.iconColor,
    this.trailing,
    this.onTap,
    this.onLongPress,
    this.enabled = true,
    this.showArrow = true,
    this.badge,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveIconColor = iconColor ?? SahoolTheme.primary;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: enabled ? onTap : null,
        onLongPress: enabled ? onLongPress : null,
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
                  child: Stack(
                    children: [
                      Center(
                        child: Icon(
                          icon,
                          color: effectiveIconColor,
                          size: 22,
                        ),
                      ),
                      // Badge
                      if (badge != null && badge! > 0)
                        Positioned(
                          top: -2,
                          right: -2,
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: const BoxDecoration(
                              color: SahoolTheme.error,
                              shape: BoxShape.circle,
                            ),
                            constraints: const BoxConstraints(
                              minWidth: 16,
                              minHeight: 16,
                            ),
                            child: Text(
                              badge! > 99 ? '99+' : badge.toString(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        ),
                    ],
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

                // Trailing widget
                if (trailing != null)
                  trailing!
                else if (showArrow && onTap != null)
                  Icon(
                    Icons.chevron_left_rounded,
                    color: isDark ? Colors.grey[600] : Colors.grey[400],
                    size: 24,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Settings Tile with value display
/// عنصر إعدادات مع عرض القيمة
class SettingsValueTile extends StatelessWidget {
  final String title;
  final String titleAr;
  final String value;
  final IconData icon;
  final Color? iconColor;
  final VoidCallback? onTap;
  final bool enabled;

  const SettingsValueTile({
    super.key,
    required this.title,
    required this.titleAr,
    required this.value,
    required this.icon,
    this.iconColor,
    this.onTap,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SettingsTile(
      title: title,
      titleAr: titleAr,
      icon: icon,
      iconColor: iconColor,
      onTap: onTap,
      enabled: enabled,
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            value,
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
    );
  }
}

/// Destructive Settings Tile (for logout, delete, etc.)
/// عنصر إعدادات للعمليات التدميرية
class DestructiveSettingsTile extends StatelessWidget {
  final String title;
  final String titleAr;
  final IconData icon;
  final VoidCallback? onTap;
  final bool enabled;

  const DestructiveSettingsTile({
    super.key,
    required this.title,
    required this.titleAr,
    required this.icon,
    this.onTap,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return SettingsTile(
      title: title,
      titleAr: titleAr,
      icon: icon,
      iconColor: SahoolTheme.error,
      onTap: onTap,
      enabled: enabled,
      showArrow: false,
    );
  }
}
