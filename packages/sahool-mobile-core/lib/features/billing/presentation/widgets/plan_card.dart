/// Plan Card Widget - بطاقة الخطة
/// Displays subscription plan with name, price, features, and upgrade action.
/// عرض خطة الاشتراك مع الاسم والسعر والميزات وزر الترقية
library;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../providers/billing_provider.dart';

/// Card displaying a subscription plan with feature comparison checkmarks
/// بطاقة عرض خطة الاشتراك مع علامات مقارنة الميزات
class PlanCard extends StatelessWidget {
  /// The plan to display
  final BillingPlan plan;

  /// Whether this plan is the user's current active plan
  final bool isCurrent;

  /// Callback when upgrade button is pressed. Null hides the button.
  final VoidCallback? onUpgrade;

  const PlanCard({
    super.key,
    required this.plan,
    required this.isCurrent,
    this.onUpgrade,
  });

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isCurrent
              ? SahoolColors.forestGreen
              : Colors.grey[300]!,
          width: isCurrent ? 2.5 : 1,
        ),
        color: isCurrent
            ? SahoolColors.forestGreen.withValues(alpha: 0.05)
            : Colors.white,
        boxShadow: isCurrent ? SahoolShadows.small : null,
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Plan Header ──────────────────────────────────────────
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: isCurrent
                        ? SahoolColors.forestGreen.withValues(alpha: 0.1)
                        : Colors.grey[100],
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    _getPlanIcon(),
                    color: isCurrent
                        ? SahoolColors.forestGreen
                        : SahoolColors.textSecondary,
                    size: 22,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        plan.nameAr,
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                          color: isCurrent
                              ? SahoolColors.forestGreen
                              : SahoolColors.textDark,
                        ),
                      ),
                      Text(
                        plan.name,
                        style: const TextStyle(
                          fontSize: 12,
                          color: SahoolColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isCurrent)
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: SahoolColors.forestGreen,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'الحالية',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 12),

            // ── Price ────────────────────────────────────────────────
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '\$${plan.priceMonthly.toStringAsFixed(0)}',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: isCurrent
                        ? SahoolColors.forestGreen
                        : SahoolColors.textDark,
                  ),
                ),
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text(
                    '/ شهرياً',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  '\$${plan.priceYearly.toStringAsFixed(0)} / سنوياً',
                  style: TextStyle(
                    color: Colors.grey[500],
                    fontSize: 12,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 14),
            Divider(color: Colors.grey[200], height: 1),
            const SizedBox(height: 14),

            // ── Feature Comparison Checkmarks ────────────────────────
            ...plan.featuresAr.map(
              (feature) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.check_circle,
                      size: 18,
                      color: isCurrent
                          ? SahoolColors.forestGreen
                          : SahoolColors.success,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        feature,
                        style: const TextStyle(fontSize: 13, height: 1.4),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // ── Upgrade Button (for non-current plans) ──────────────
            if (!isCurrent && onUpgrade != null) ...[
              const SizedBox(height: 14),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: onUpgrade,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: SahoolColors.forestGreen,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: const Text(
                    'ترقية الآن',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  IconData _getPlanIcon() {
    switch (plan.tier) {
      case PlanTier.starter:
        return Icons.rocket_launch;
      case PlanTier.professional:
        return Icons.business;
      case PlanTier.enterprise:
        return Icons.corporate_fare;
    }
  }
}
