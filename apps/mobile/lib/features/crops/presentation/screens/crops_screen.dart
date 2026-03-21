/// Crops Management Screen
/// شاشة إدارة المحاصيل
///
/// Main screen for managing active crops with:
/// - List/grid of active crops with health indicators
/// - Growth stage timeline for each crop
/// - Quick actions: add crop, record observation, view history
/// - Arabic/English bilingual
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../../data/models/crop_model.dart';
import '../../data/crop_helper.dart';
import '../providers/crops_provider.dart';
import '../widgets/crop_card.dart';

/// Main crops management screen
/// شاشة إدارة المحاصيل الرئيسية
class CropsScreen extends ConsumerStatefulWidget {
  const CropsScreen({super.key});

  @override
  ConsumerState<CropsScreen> createState() => _CropsScreenState();
}

class _CropsScreenState extends ConsumerState<CropsScreen> {
  bool _isGridView = false;

  @override
  Widget build(BuildContext context) {
    final cropsState = ref.watch(cropsProvider);

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: _buildAppBar(cropsState),
      body: cropsState.isLoading
          ? const Center(
              child: CircularProgressIndicator(
                  color: SahoolColors.forestGreen),
            )
          : cropsState.error != null
              ? _buildErrorState(cropsState.error!)
              : _buildBody(cropsState),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddCropSheet(context),
        backgroundColor: SahoolColors.forestGreen,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text(
          'Add Crop | اضافة محصول',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(CropsState cropsState) {
    return AppBar(
      title: const Text('Crops Management | ادارة المحاصيل'),
      backgroundColor: Colors.white,
      foregroundColor: SahoolColors.forestGreen,
      elevation: 0,
      actions: [
        // Toggle list/grid view
        IconButton(
          icon: Icon(_isGridView ? Icons.list : Icons.grid_view),
          onPressed: () => setState(() => _isGridView = !_isGridView),
          tooltip: 'Toggle view | تبديل العرض',
        ),
        IconButton(
          icon: const Icon(Icons.filter_list),
          onPressed: () => _showFilterSheet(context),
          tooltip: 'Filter | فلتر',
        ),
      ],
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: SahoolColors.danger),
          const SizedBox(height: 16),
          Text(
            'Error loading crops\nخطا في تحميل المحاصيل',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref.read(cropsProvider.notifier).loadCrops(),
            child: const Text('Retry | اعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(CropsState cropsState) {
    return RefreshIndicator(
      onRefresh: () => ref.read(cropsProvider.notifier).loadCrops(),
      color: SahoolColors.forestGreen,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Summary header
          _buildSummaryRow(cropsState),
          const SizedBox(height: 16),

          // Quick actions
          _buildQuickActions(),
          const SizedBox(height: 20),

          // Section title
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Active Crops | المحاصيل النشطة',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.forestGreen,
                ),
              ),
              Text(
                '${cropsState.activeCrops.length} crops | محصول',
                style: TextStyle(fontSize: 13, color: Colors.grey[500]),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Crop list or grid
          if (cropsState.activeCrops.isEmpty)
            _buildEmptyState()
          else
            ..._buildCropList(cropsState),

          const SizedBox(height: 80), // Space for FAB
        ],
      ),
    );
  }

  // ===========================================================================
  // Summary Row
  // صف الملخص
  // ===========================================================================

  Widget _buildSummaryRow(CropsState cropsState) {
    final totalArea = cropsState.activeCrops.fold<double>(
        0.0, (sum, c) => sum + c.areaHectares);
    final healthyCrops = cropsState.activeCrops
        .where((c) =>
            c.healthStatus == 'healthy' || c.healthStatus == 'good')
        .length;

    return Row(
      children: [
        Expanded(
          child: _SummaryCard(
            icon: Icons.eco,
            value: '${cropsState.activeCrops.length}',
            label: 'Active | نشط',
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _SummaryCard(
            icon: Icons.landscape,
            value: '${totalArea.toStringAsFixed(1)} ha',
            label: 'Total Area | المساحة',
            color: SahoolColors.earthBrown,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _SummaryCard(
            icon: Icons.favorite,
            value: '$healthyCrops',
            label: 'Healthy | صحي',
            color: SahoolColors.success,
          ),
        ),
      ],
    );
  }

  // ===========================================================================
  // Quick Actions
  // إجراءات سريعة
  // ===========================================================================

  Widget _buildQuickActions() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _QuickAction(
            icon: Icons.add_circle_outline,
            label: 'Add Crop\nاضافة محصول',
            color: SahoolColors.forestGreen,
            onTap: () => _showAddCropSheet(context),
          ),
          const SizedBox(width: 12),
          _QuickAction(
            icon: Icons.edit_note,
            label: 'Record Observation\nتسجيل ملاحظة',
            color: SahoolColors.info,
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('تسجيل الملاحظات - قريباً'),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
          ),
          const SizedBox(width: 12),
          _QuickAction(
            icon: Icons.history,
            label: 'Crop History\nتاريخ المحاصيل',
            color: SahoolColors.harvestGold,
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('تاريخ المحاصيل - قريباً'),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
          ),
          const SizedBox(width: 12),
          _QuickAction(
            icon: Icons.analytics,
            label: 'Analytics\nالتحليلات',
            color: SahoolColors.sageGreen,
            onTap: () {
              Navigator.pushNamed(context, '/analytics');
            },
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // Crop List
  // قائمة المحاصيل
  // ===========================================================================

  List<Widget> _buildCropList(CropsState cropsState) {
    return cropsState.activeCrops.map((activeCrop) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: CropCard(
          activeCrop: activeCrop,
          onTap: () => _showCropDetails(context, activeCrop),
        ),
      );
    }).toList();
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(40),
      child: Column(
        children: [
          Icon(Icons.eco, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            'No active crops\nلا توجد محاصيل نشطة',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add your first crop to get started\nاضف اول محصول للبدء',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: Colors.grey[400]),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // Crop Details Bottom Sheet
  // نافذة تفاصيل المحصول
  // ===========================================================================

  Future<void> _showCropDetails(BuildContext context, ActiveCrop crop) async {
    final recommendations =
        await ref.read(cropsProvider.notifier).getRecommendations(crop.id);

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        height: MediaQuery.of(context).size.height * 0.75,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            // Handle
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

            // Crop header
            Row(
              children: [
                Text(
                  CropHelper.getCropEmoji(crop.crop.code),
                  style: const TextStyle(fontSize: 40),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${crop.crop.nameAr} (${crop.crop.nameEn})',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${crop.variety} - ${crop.fieldName}',
                        style: TextStyle(
                            color: Colors.grey[600], fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Info grid
            Row(
              children: [
                Expanded(
                  child: _DetailItem(
                    label: 'Stage | المرحلة',
                    value: crop.growthStageAr,
                  ),
                ),
                Expanded(
                  child: _DetailItem(
                    label: 'NDVI',
                    value: crop.ndviValue.toStringAsFixed(2),
                  ),
                ),
                Expanded(
                  child: _DetailItem(
                    label: 'Health | الصحة',
                    value: crop.healthStatusAr,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _DetailItem(
                    label: 'Area | المساحة',
                    value: '${crop.areaHectares} ha',
                  ),
                ),
                Expanded(
                  child: _DetailItem(
                    label: 'Days Planted | ايام',
                    value: '${crop.daysSincePlanting}',
                  ),
                ),
                Expanded(
                  child: _DetailItem(
                    label: 'To Harvest | للحصاد',
                    value: crop.daysToHarvest != null
                        ? '${crop.daysToHarvest} days'
                        : '-',
                  ),
                ),
              ],
            ),

            const Divider(height: 32),

            // Recommendations
            const Text(
              'Recommendations | التوصيات',
              style:
                  TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...recommendations.map((rec) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.lightbulb_outline,
                          size: 18, color: SahoolColors.harvestGold),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          rec,
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  // ===========================================================================
  // Add Crop Bottom Sheet
  // نافذة اضافة محصول
  // ===========================================================================

  void _showAddCropSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
            const Text(
              'Add New Crop | اضافة محصول جديد',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),

            // Crop selection (simplified categories)
            const Text(
              'Select Crop | اختر المحصول',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: GridView.count(
                crossAxisCount: 3,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                children: [
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('WHEAT'),
                    name: 'Wheat | قمح',
                    onTap: () => _addCropAndClose(ctx, 'WHEAT'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('BARLEY'),
                    name: 'Barley | شعير',
                    onTap: () => _addCropAndClose(ctx, 'BARLEY'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('TOMATO'),
                    name: 'Tomato | طماطم',
                    onTap: () => _addCropAndClose(ctx, 'TOMATO'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('CORN'),
                    name: 'Corn | ذرة',
                    onTap: () => _addCropAndClose(ctx, 'CORN'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('POTATO'),
                    name: 'Potato | بطاطس',
                    onTap: () => _addCropAndClose(ctx, 'POTATO'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('DATE_PALM'),
                    name: 'Date Palm | نخيل',
                    onTap: () => _addCropAndClose(ctx, 'DATE_PALM'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('ONION'),
                    name: 'Onion | بصل',
                    onTap: () => _addCropAndClose(ctx, 'ONION'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('ALFALFA'),
                    name: 'Alfalfa | برسيم',
                    onTap: () => _addCropAndClose(ctx, 'ALFALFA'),
                  ),
                  _CropOption(
                    emoji: CropHelper.getCropEmoji('COFFEE'),
                    name: 'Coffee | بن',
                    onTap: () => _addCropAndClose(ctx, 'COFFEE'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _addCropAndClose(BuildContext ctx, String cropCode) {
    ref.read(cropsProvider.notifier).addCrop(
          fieldId: 'field_new',
          fieldName: 'New Field | حقل جديد',
          crop: Crop(
            code: cropCode,
            nameEn: cropCode,
            nameAr: CropHelper.getCropNameAr(cropCode),
            scientificName: '',
            category: CropCategory.cereals,
            growthHabit: GrowthHabit.annual,
            growingSeasonDays: 120,
            optimalTempMin: 15,
            optimalTempMax: 30,
            waterRequirement: WaterRequirement.medium,
            baseYieldTonHa: 3.0,
          ),
          areaHectares: 1.0,
        );
    Navigator.pop(ctx);
  }

  void _showFilterSheet(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Filter coming soon | الفلتر قريبا'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

// =============================================================================
// Helper Widgets
// عناصر مساعدة
// =============================================================================

class _SummaryCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _SummaryCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 10, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 100,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 6),
            Text(
              label,
              style: TextStyle(fontSize: 10, color: color),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailItem extends StatelessWidget {
  final String label;
  final String value;

  const _DetailItem({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.grey[500]),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _CropOption extends StatelessWidget {
  final String emoji;
  final String name;
  final VoidCallback onTap;

  const _CropOption({
    required this.emoji,
    required this.name,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: SahoolColors.paleOlive.withOpacity(0.5),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: SahoolColors.sageGreen.withOpacity(0.3)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 32)),
            const SizedBox(height: 4),
            Text(
              name,
              style: const TextStyle(fontSize: 10),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
