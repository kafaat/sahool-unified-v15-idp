/// SAHOOL Sell Harvest Dialog
/// نافذة بيع الحصاد الذكي - تحويل توقعات الذكاء الاصطناعي إلى منتج للبيع
///
/// Features:
/// - Display AI yield predictions
/// - Set price and quality
/// - Submit to marketplace

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/config/api_config.dart';
import '../data/market_repository.dart';

/// مزود بيانات الحصاد المتوقع (من yield-engine)
final yieldPredictionProvider = StateProvider<Map<String, dynamic>?>((ref) => null);

/// إظهار نافذة بيع الحصاد
void showSellHarvestDialog(BuildContext context, WidgetRef ref, {Map<String, dynamic>? yieldData}) {
  // استخدام بيانات تجريبية إذا لم تتوفر بيانات فعلية
  final data = yieldData ?? {
    'crop': 'Wheat',
    'cropAr': 'قمح',
    'predictedYieldTons': 12.5,
    'marketPrice': 320000.0, // سعر الطن بالريال اليمني
    'harvestDate': '2025-02-15',
    'qualityGrade': 'A',
    'governorate': 'صنعاء',
    'confidence': 0.87,
  };

  showDialog(
    context: context,
    builder: (context) => _SellHarvestDialog(yieldData: data),
  );
}

class _SellHarvestDialog extends ConsumerStatefulWidget {
  final Map<String, dynamic> yieldData;

  const _SellHarvestDialog({required this.yieldData});

  @override
  ConsumerState<_SellHarvestDialog> createState() => _SellHarvestDialogState();
}

class _SellHarvestDialogState extends ConsumerState<_SellHarvestDialog> {
  late double _pricePerTon;
  late double _quantity;
  String _qualityGrade = 'A';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _pricePerTon = (widget.yieldData['marketPrice'] as num).toDouble();
    _quantity = (widget.yieldData['predictedYieldTons'] as num).toDouble();
    _qualityGrade = widget.yieldData['qualityGrade'] ?? 'A';
  }

  double get _totalValue => _pricePerTon * _quantity;

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        child: Container(
          padding: const EdgeInsets.all(24),
          constraints: const BoxConstraints(maxWidth: 400),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: SahoolColors.forestGreen.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.auto_graph,
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
                            'بيع الحصاد المتوقع',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            'Smart B2B Harvest Sale',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                // AI Prediction Banner
                Container(
                  padding: const EdgeInsets.all(16),
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
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.psychology, size: 20, color: SahoolColors.forestGreen),
                          const SizedBox(width: 8),
                          const Text(
                            'توقع الذكاء الاصطناعي',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: SahoolColors.forestGreen,
                            ),
                          ),
                          const Spacer(),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: SahoolColors.forestGreen,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '${((widget.yieldData['confidence'] as num) * 100).toInt()}% دقة',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'بناءً على تحليل صور الأقمار الصناعية والمؤشرات الزراعية',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // Yield Info
                _InfoRow(
                  label: 'المحصول',
                  value: widget.yieldData['cropAr'] ?? widget.yieldData['crop'],
                  icon: Icons.grass,
                ),
                _InfoRow(
                  label: 'المحافظة',
                  value: widget.yieldData['governorate'] ?? 'غير محدد',
                  icon: Icons.location_on,
                ),
                _InfoRow(
                  label: 'تاريخ الحصاد المتوقع',
                  value: widget.yieldData['harvestDate'] ?? 'غير محدد',
                  icon: Icons.calendar_today,
                ),

                const Divider(height: 32),

                // Editable Fields
                const Text(
                  'تفاصيل العرض',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 16),

                // Quantity Slider
                _SliderField(
                  label: 'الكمية (طن)',
                  value: _quantity,
                  min: 1,
                  max: (widget.yieldData['predictedYieldTons'] as num).toDouble() * 1.2,
                  onChanged: (value) => setState(() => _quantity = value),
                  suffix: ' طن',
                ),

                const SizedBox(height: 16),

                // Price Input
                _SliderField(
                  label: 'السعر (ريال/طن)',
                  value: _pricePerTon,
                  min: _pricePerTon * 0.7,
                  max: _pricePerTon * 1.3,
                  onChanged: (value) => setState(() => _pricePerTon = value),
                  suffix: ' ر.ي',
                  divisions: 20,
                ),

                const SizedBox(height: 16),

                // Quality Grade
                Row(
                  children: [
                    const Text('درجة الجودة:'),
                    const SizedBox(width: 16),
                    Expanded(
                      child: SegmentedButton<String>(
                        segments: const [
                          ButtonSegment(value: 'A', label: Text('A')),
                          ButtonSegment(value: 'B', label: Text('B')),
                          ButtonSegment(value: 'C', label: Text('C')),
                        ],
                        selected: {_qualityGrade},
                        onSelectionChanged: (selected) {
                          setState(() => _qualityGrade = selected.first);
                        },
                        style: ButtonStyle(
                          backgroundColor: WidgetStateProperty.resolveWith((states) {
                            if (states.contains(WidgetState.selected)) {
                              return SahoolColors.forestGreen;
                            }
                            return null;
                          }),
                        ),
                      ),
                    ),
                  ],
                ),

                const Divider(height: 32),

                // Total Value
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: SahoolColors.harvestGold.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: SahoolColors.harvestGold.withOpacity(0.3)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'العائد المتوقع',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${_formatNumber(_totalValue)} ر.ي',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.forestGreen,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Info Note
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.blue, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'سيتم عرض محصولك للتجار والمصانع للشراء المسبق',
                          style: TextStyle(fontSize: 12, color: Colors.blue),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Action Buttons
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pop(context),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text('إلغاء'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 2,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _submitListing,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: SahoolColors.forestGreen,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.store, size: 20),
                                  SizedBox(width: 8),
                                  Text('اعرض للبيع'),
                                ],
                              ),
                      ),
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

  Future<void> _submitListing() async {
    setState(() => _isLoading = true);

    try {
      final repo = ref.read(marketRepoProvider);
      final userId = ref.read(currentUserIdProvider);

      final result = await repo.listHarvest(
        userId: userId,
        crop: widget.yieldData['crop'] ?? 'Unknown',
        cropAr: widget.yieldData['cropAr'] ?? widget.yieldData['crop'] ?? 'غير معروف',
        predictedYieldTons: _quantity,
        pricePerTon: _pricePerTon,
        harvestDate: widget.yieldData['harvestDate'],
        qualityGrade: _qualityGrade,
        governorate: widget.yieldData['governorate'],
      );

      if (!mounted) return;

      result.when(
        success: (product) {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.white),
                  SizedBox(width: 8),
                  Text('تم إنشاء إعلان البيع بنجاح!'),
                ],
              ),
              backgroundColor: SahoolColors.forestGreen,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          );
        },
        failure: (message, _, __) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('فشل: $message'),
              backgroundColor: Colors.red,
            ),
          );
        },
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
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

/// صف معلومات
class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _InfoRow({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 12),
          Text(label, style: TextStyle(color: Colors.grey[600])),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

/// حقل بشريط تمرير
class _SliderField extends StatelessWidget {
  final String label;
  final double value;
  final double min;
  final double max;
  final ValueChanged<double> onChanged;
  final String suffix;
  final int? divisions;

  const _SliderField({
    required this.label,
    required this.value,
    required this.min,
    required this.max,
    required this.onChanged,
    required this.suffix,
    this.divisions,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: TextStyle(color: Colors.grey[600])),
            Text(
              '${value.toStringAsFixed(1)}$suffix',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: divisions,
          activeColor: SahoolColors.forestGreen,
          onChanged: onChanged,
        ),
      ],
    );
  }
}
