/// Plan Card Widget - Displays subscription plan details
/// بطاقة الخطة - عرض تفاصيل خطة الاشتراك
import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../providers/billing_provider.dart';

/// Card displaying a subscription plan with features and pricing
/// بطاقة عرض خطة الاشتراك مع الميزات والأسعار
class PlanCard extends StatelessWidget {
  final BillingPlan plan;
  final bool isCurrentPlan;
  final VoidCallback onUpgrade;

  const PlanCard({
    super.key,
    required this.plan,
    required this.isCurrentPlan,
    required this.onUpgrade,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isCurrentPlan ? SahoolColors.forestGreen : Colors.grey[300]!,
          width: isCurrentPlan ? 2 : 1,
        ),
        color: isCurrentPlan ? SahoolColors.forestGreen.withOpacity(0.05) : Colors.white,
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Plan header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      _getPlanIcon(),
                      color: isCurrentPlan ? SahoolColors.forestGreen : Colors.grey[600],
                    ),
                    const SizedBox(width: 8),
                    Text(
                      plan.name,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: isCurrentPlan ? SahoolColors.forestGreen : null,
                      ),
                    ),
                  ],
                ),
                if (isCurrentPlan)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: SahoolColors.forestGreen,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'الحالية',
                      style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),

            // Price
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${plan.priceMonthly}',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: isCurrentPlan ? SahoolColors.forestGreen : null,
                  ),
                ),
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 3),
                  child: Text(
                    'ريال/شهر',
                    style: TextStyle(color: Colors.grey[600], fontSize: 13),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Features
            ...plan.features.map((feature) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    children: [
                      Icon(
                        Icons.check_circle,
                        size: 18,
                        color: isCurrentPlan ? SahoolColors.forestGreen : SahoolColors.success,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(feature, style: const TextStyle(fontSize: 13)),
                      ),
                    ],
                  ),
                )),

            // Upgrade button
            if (!isCurrentPlan) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: onUpgrade,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: SahoolColors.forestGreen,
                    side: const BorderSide(color: SahoolColors.forestGreen),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  child: const Text('ترقية'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  IconData _getPlanIcon() {
    return switch (plan.id) {
      'starter' => Icons.rocket_launch,
      'professional' => Icons.business,
      'enterprise' => Icons.corporate_fare,
      _ => Icons.card_membership,
    };
  }
}
