/// SAHOOL Smart Sell Harvest Sheet
/// نافذة بيع الحصاد الذكي - Bottom Sheet احترافي
///
/// Features:
/// - Professional invoice-like design
/// - AI yield prediction display
/// - Animated loading state
/// - Integration with MarketNotifier

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../logic/market_notifier.dart';
import '../data/market_repository.dart';

// =============================================================================
// Main Entry Point
// =============================================================================

/// إظهار نافذة بيع الحصاد الذكي
void showSellHarvestDialog(BuildContext context, WidgetRef ref, {Map<String, dynamic>? yieldData}) {
  // استخدام بيانات تجريبية إذا لم تتوفر بيانات فعلية
  final data = yieldData ?? {
    'crop_type': 'Wheat',
    'crop_type_ar': 'قمح',
    'predicted_yield_tons': 12.5,
    'price_per_ton': 320000.0, // سعر الطن بالريال اليمني
    'harvest_date': '2025-02-15',
    'quality_grade': 'A',
    'governorate': 'صنعاء',
    'ai_confidence': 0.87,
    'total_value': 12.5 * 320000.0,
  };

  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
    ),
    builder: (context) => Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: _SmartSellHarvestSheet(yieldData: data),
    ),
  );
}

// =============================================================================
// Smart Sell Harvest Sheet
// =============================================================================

class _SmartSellHarvestSheet extends ConsumerWidget {
  final Map<String, dynamic> yieldData;

  const _SmartSellHarvestSheet({required this.yieldData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(marketNotifierProvider);

    // الاستماع للتغييرات لإغلاق النافذة عند النجاح
    ref.listen(marketNotifierProvider, (previous, next) {
      if (next.status == MarketStatus.success) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 8),
                Expanded(child: Text('تم طرح المحصول في السوق بنجاح!')),
              ],
            ),
            backgroundColor: SahoolColors.forestGreen,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            margin: const EdgeInsets.all(16),
          ),
        );
        // تحديث قائمة المنتجات
        ref.invalidate(productsFutureProvider);
      } else if (next.status == MarketStatus.error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next.errorMessage ?? 'حدث خطأ'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    });

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
        ),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Handle bar
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Header
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            SahoolColors.forestGreen.withOpacity(0.1),
                            SahoolColors.harvestGold.withOpacity(0.1),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.rocket_launch,
                        color: SahoolColors.forestGreen,
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'ملخص البيع الذكي',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            'سيتم عرض هذه الكمية للمشترين المعتمدين فوراً',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // AI Badge
                _AIConfidenceBadge(
                  confidence: (yieldData['ai_confidence'] ?? yieldData['confidence'] ?? 0.85) as double,
                ),

                const SizedBox(height: 24),

                // Invoice Card
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[50],
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey[200]!),
                  ),
                  child: Column(
                    children: [
                      _InvoiceRow(
                        label: 'المحصول',
                        value: yieldData['crop_type_ar'] ?? yieldData['cropAr'] ?? 'قمح',
                        icon: Icons.grass,
                      ),
                      const Divider(height: 24),
                      _InvoiceRow(
                        label: 'الكمية المتوقعة',
                        value: '${yieldData['predicted_yield_tons'] ?? yieldData['predictedYieldTons']} طن',
                        icon: Icons.scale,
                      ),
                      const Divider(height: 24),
                      _InvoiceRow(
                        label: 'سعر السوق الحالي',
                        value: '${_formatNumber((yieldData['price_per_ton'] ?? yieldData['marketPrice'] ?? 0).toDouble())} ر.ي/طن',
                        icon: Icons.trending_up,
                      ),
                      const Divider(height: 24),
                      _InvoiceRow(
                        label: 'المحافظة',
                        value: yieldData['governorate'] ?? 'غير محدد',
                        icon: Icons.location_on,
                      ),
                      const Divider(height: 24),
                      _InvoiceRow(
                        label: 'موعد الحصاد',
                        value: yieldData['harvest_date'] ?? yieldData['harvestDate'] ?? 'قريباً',
                        icon: Icons.calendar_today,
                      ),
                      const Divider(height: 24),
                      _InvoiceRow(
                        label: 'درجة الجودة',
                        value: yieldData['quality_grade'] ?? yieldData['qualityGrade'] ?? 'A',
                        icon: Icons.star,
                        valueColor: SahoolColors.harvestGold,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Total Value Card
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        SahoolColors.forestGreen.withOpacity(0.1),
                        SahoolColors.harvestGold.withOpacity(0.1),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: SahoolColors.forestGreen.withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'العائد التقديري',
                            style: TextStyle(
                              color: SahoolColors.forestGreen,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            'Estimated Revenue',
                            style: TextStyle(
                              color: Colors.grey,
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                      Text(
                        '${_formatNumber(_calculateTotal(yieldData))} ر.ي',
                        style: const TextStyle(
                          color: SahoolColors.forestGreen,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Info Note
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue.withOpacity(0.2)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.blue, size: 20),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'سيتم إرسال إشعارات للتجار والمصانع المهتمين بمنتجك. ستتلقى عروض الشراء في المحفظة.',
                          style: TextStyle(fontSize: 12, color: Colors.blue),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 32),

                // Submit Button
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: state.isLoading
                        ? null
                        : () => ref.read(marketNotifierProvider.notifier).sellHarvest(yieldData),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: SahoolColors.forestGreen,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 0,
                    ),
                    child: state.isLoading
                        ? const SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.rocket_launch),
                              SizedBox(width: 8),
                              Text(
                                'تأكيد وعرض للبيع',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                  ),
                ),

                const SizedBox(height: 16),

                // Cancel Button
                SizedBox(
                  width: double.infinity,
                  child: TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text(
                      'إلغاء',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                ),

                // Bottom padding for safe area
                SizedBox(height: MediaQuery.of(context).padding.bottom),
              ],
            ),
          ),
        ),
      ),
    );
  }

  double _calculateTotal(Map<String, dynamic> data) {
    final quantity = (data['predicted_yield_tons'] ?? data['predictedYieldTons'] ?? 0).toDouble();
    final price = (data['price_per_ton'] ?? data['marketPrice'] ?? 0).toDouble();
    return quantity * price;
  }

  String _formatNumber(double number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(0)}K';
    }
    return number.toStringAsFixed(0);
  }
}

// =============================================================================
// AI Confidence Badge
// =============================================================================

class _AIConfidenceBadge extends StatelessWidget {
  final double confidence;

  const _AIConfidenceBadge({required this.confidence});

  @override
  Widget build(BuildContext context) {
    final percentage = (confidence * 100).toInt();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            SahoolColors.forestGreen.withOpacity(0.05),
            SahoolColors.harvestGold.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: SahoolColors.forestGreen.withOpacity(0.2),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: SahoolColors.forestGreen.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.psychology,
              color: SahoolColors.forestGreen,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'توقع الذكاء الاصطناعي',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.forestGreen,
                    fontSize: 13,
                  ),
                ),
                Text(
                  'بناءً على صور الأقمار الصناعية والبيانات الزراعية',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: _getConfidenceColor(confidence),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              '$percentage% دقة',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return SahoolColors.forestGreen;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }
}

// =============================================================================
// Invoice Row Widget
// =============================================================================

class _InvoiceRow extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? valueColor;

  const _InvoiceRow({
    required this.label,
    required this.value,
    required this.icon,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.grey[400]),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 15,
            color: valueColor,
          ),
        ),
      ],
    );
  }
}
