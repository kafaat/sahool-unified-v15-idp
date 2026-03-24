import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';

/// Settings Section Widget
/// قسم الإعدادات - يجمع الإعدادات المتعلقة ببعضها
class SettingsSection extends StatelessWidget {
  /// Section title in English
  final String title;

  /// Section title in Arabic
  final String titleAr;

  /// Child widgets (usually SettingsTile widgets)
  final List<Widget> children;

  /// Optional subtitle for additional context
  final String? subtitle;

  /// Optional icon for section header
  final IconData? icon;

  /// Whether to show divider between children
  final bool showDividers;

  const SettingsSection({
    super.key,
    required this.title,
    required this.titleAr,
    required this.children,
    this.subtitle,
    this.icon,
    this.showDividers = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section Header
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
          child: Row(
            children: [
              if (icon != null) ...[
                Icon(
                  icon,
                  size: 18,
                  color: SahoolTheme.primary,
                ),
                const SizedBox(width: 8),
              ],
              Text(
                titleAr, // Arabic takes priority in RTL
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: SahoolTheme.primary,
                  fontSize: 14,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
        ),

        // Optional subtitle
        if (subtitle != null)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
            child: Text(
              subtitle!,
              style: TextStyle(
                color: isDark ? Colors.grey[400] : Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ),

        // Section content card
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: isDark ? Colors.grey[900] : Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: isDark ? 0.3 : 0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Column(
              children: _buildChildren(),
            ),
          ),
        ),
      ],
    );
  }

  List<Widget> _buildChildren() {
    if (!showDividers || children.isEmpty) {
      return children;
    }

    final List<Widget> result = [];
    for (int i = 0; i < children.length; i++) {
      result.add(children[i]);
      if (i < children.length - 1) {
        result.add(
          const Divider(
            height: 1,
            indent: 16,
            endIndent: 16,
          ),
        );
      }
    }
    return result;
  }
}

/// Compact Settings Section without card wrapper
/// قسم إعدادات مضغوط بدون بطاقة
class CompactSettingsSection extends StatelessWidget {
  final String titleAr;
  final List<Widget> children;

  const CompactSettingsSection({
    super.key,
    required this.titleAr,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            titleAr,
            style: TextStyle(
              fontWeight: FontWeight.w600,
              color: Colors.grey[600],
              fontSize: 13,
              letterSpacing: 0.3,
            ),
          ),
        ),
        ...children,
      ],
    );
  }
}
