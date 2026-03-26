import 'package:flutter/material.dart';
import 'sahool_theme.dart';
import '../accessibility/semantics_helper.dart';

/// بطاقة عضوية - تصميم Bento Grid
/// OrganicCard - Rounded corners, soft shadows, natural feel
class OrganicCard extends StatelessWidget {
  final Widget child;
  final Color? color;
  final EdgeInsetsGeometry? padding;
  final bool isPrimary;
  final VoidCallback? onTap;
  final double borderRadius;

  const OrganicCard({
    super.key,
    required this.child,
    this.color,
    this.padding,
    this.isPrimary = false,
    this.onTap,
    this.borderRadius = 28,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor = color ?? (isPrimary ? SahoolColors.forestGreen : Colors.white);
    final textColor = isPrimary ? Colors.white : SahoolColors.forestGreen;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: padding ?? const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(borderRadius),
          boxShadow: [
            BoxShadow(
              color: bgColor.withValues(alpha: 0.15),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: DefaultTextStyle(
          style: TextStyle(color: textColor),
          child: IconTheme(
            data: IconThemeData(color: textColor),
            child: child,
          ),
        ),
      ),
    );
  }
}

/// شارة الحالة - لعرض حالة الحقل أو الجهاز
/// Status Badge with Accessibility Support
class StatusBadge extends StatelessWidget {
  final String label;
  final Color color;
  final IconData? icon;
  final bool isSmall;
  final String? semanticLabel;

  const StatusBadge({
    super.key,
    required this.label,
    required this.color,
    this.icon,
    this.isSmall = false,
    this.semanticLabel,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: semanticLabel ?? 'الحالة: $label',
      child: Container(
        padding: EdgeInsets.symmetric(
          horizontal: isSmall ? 8 : 12,
          vertical: isSmall ? 4 : 6,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              ExcludeSemantics(
                child: Icon(icon, size: isSmall ? 12 : 14, color: color),
              ),
              const SizedBox(width: 4),
            ],
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: isSmall ? 10 : 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// بطاقة المقاييس - لعرض الإحصائيات
class MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String? subtitle;
  final IconData icon;
  final Color? iconColor;
  final String? trend;
  final bool isPositiveTrend;

  const MetricCard({
    super.key,
    required this.title,
    required this.value,
    this.subtitle,
    required this.icon,
    this.iconColor,
    this.trend,
    this.isPositiveTrend = true,
  });

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: iconColor ?? SahoolColors.sageGreen),
              Text(
                title,
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const Spacer(),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: SahoolColors.forestGreen,
                    ),
                  ),
                  if (trend != null) ...[
                    const SizedBox(width: 4),
                    Icon(
                      isPositiveTrend ? Icons.arrow_upward : Icons.arrow_downward,
                      size: 14,
                      color: isPositiveTrend ? SahoolColors.sageGreen : Colors.red,
                    ),
                    Text(
                      trend!,
                      style: TextStyle(
                        fontSize: 12,
                        color: isPositiveTrend ? SahoolColors.sageGreen : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ],
              ),
              if (subtitle != null)
                Text(
                  subtitle!,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[500],
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/// شريط التنقل العائم
/// Floating Navigation Bar with Accessibility Support
class FloatingNavBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const FloatingNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'شريط التنقل الرئيسي',
      child: Container(
        margin: const EdgeInsets.only(left: 24, right: 24, bottom: 24),
        height: 70,
        decoration: BoxDecoration(
          color: SahoolColors.forestGreen,
          borderRadius: BorderRadius.circular(35),
          boxShadow: [
            BoxShadow(
              color: SahoolColors.forestGreen.withValues(alpha: 0.3),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _NavItem(
              icon: Icons.home_filled,
              label: SahoolSemantics.homeTab,
              isSelected: currentIndex == 0,
              onTap: () => onTap(0),
            ),
            _NavItem(
              icon: Icons.analytics_outlined,
              label: SahoolSemantics.monitorTab,
              isSelected: currentIndex == 1,
              onTap: () => onTap(1),
            ),
            // زر الإضافة المركزي - Central add button
            Semantics(
              label: SahoolSemantics.addFieldButton,
              button: true,
              child: GestureDetector(
                onTap: () => onTap(-1), // -1 للإضافة
                child: Container(
                  width: kMinTouchTargetSize,
                  height: kMinTouchTargetSize,
                  decoration: BoxDecoration(
                    color: SahoolColors.harvestGold,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: SahoolColors.forestGreen,
                      width: 4,
                    ),
                  ),
                  child: const Icon(
                    Icons.add,
                    color: SahoolColors.forestGreen,
                  ),
                ),
              ),
            ),
            _NavItem(
              icon: Icons.chat_bubble_outline,
              label: 'الرسائل، تبويب',
              isSelected: currentIndex == 2,
              onTap: () => onTap(2),
            ),
            _NavItem(
              icon: Icons.person_outline,
              label: SahoolSemantics.profileTab,
              isSelected: currentIndex == 3,
              onTap: () => onTap(3),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      button: true,
      selected: isSelected,
      hint: isSelected ? 'محدد حالياً' : null,
      child: SizedBox(
        width: kMinTouchTargetSize,
        height: kMinTouchTargetSize,
        child: IconButton(
          icon: Icon(
            icon,
            color: isSelected ? Colors.white : Colors.white70,
          ),
          onPressed: onTap,
          tooltip: label,
        ),
      ),
    );
  }
}

/// رأس الترحيب مع الطقس
class WelcomeHeader extends StatelessWidget {
  final String greeting;
  final String userName;
  final String temperature;
  final Widget? syncIndicator;

  const WelcomeHeader({
    super.key,
    required this.greeting,
    required this.userName,
    required this.temperature,
    this.syncIndicator,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              greeting,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Colors.grey,
                  ),
            ),
            Text(
              userName,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                    color: SahoolColors.forestGreen,
                  ),
            ),
          ],
        ),
        // كبسولة الطقس والمزامنة
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.grey.withValues(alpha: 0.1)),
          ),
          child: Row(
            children: [
              if (syncIndicator != null) ...[
                syncIndicator!,
                Container(
                  height: 20,
                  width: 1,
                  color: Colors.grey[300],
                  margin: const EdgeInsets.symmetric(horizontal: 8),
                ),
              ],
              const Icon(
                Icons.wb_sunny_rounded,
                color: SahoolColors.harvestGold,
                size: 20,
              ),
              const SizedBox(width: 4),
              Text(
                temperature,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
