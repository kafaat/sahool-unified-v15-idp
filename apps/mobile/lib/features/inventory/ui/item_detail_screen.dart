/// Item Detail Screen - شاشة تفاصيل العنصر
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../data/inventory_models.dart';
import '../providers/inventory_providers.dart';
import '../widgets/movement_tile.dart';
import '../widgets/stock_level_indicator.dart';
import '../../../core/performance/image_cache_manager.dart';

/// شاشة تفاصيل عنصر المخزون
class ItemDetailScreen extends ConsumerWidget {
  final String itemId;

  const ItemDetailScreen({
    super.key,
    required this.itemId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final itemAsync = ref.watch(inventoryItemDetailsProvider(itemId));
    final movementsAsync = ref.watch(stockMovementsProvider(itemId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل العنصر'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              // Navigate to edit screen
            },
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () => _showDeleteConfirmation(context, ref),
          ),
        ],
      ),
      body: itemAsync.when(
        data: (item) => _buildContent(context, ref, item, movementsAsync),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
              const SizedBox(height: 16),
              Text('فشل في تحميل التفاصيل'),
              const SizedBox(height: 8),
              Text(error.toString()),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(inventoryItemDetailsProvider(itemId)),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    InventoryItem item,
    AsyncValue<List<StockMovement>> movementsAsync,
  ) {
    final locale = Localizations.localeOf(context).languageCode;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // صورة العنصر
          if (item.imageUrl != null)
            CachedNetworkImage(
              imageUrl: item.imageUrl!,
              cacheManager: SahoolImageCacheManager.instance.cacheManager,
              height: 200,
              width: double.infinity,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                height: 200,
                color: Colors.grey.shade100,
                child: Center(
                  child: CircularProgressIndicator(
                    color: Theme.of(context).primaryColor,
                  ),
                ),
              ),
              errorWidget: (context, url, error) => _buildImagePlaceholder(context, item),
            )
          else
            _buildImagePlaceholder(context, item),

          // معلومات أساسية
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // الاسم
                Text(
                  item.getDisplayName(locale),
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8),

                // الفئة والوحدة
                Row(
                  children: [
                    Chip(
                      label: Text(item.category.getName(locale)),
                      avatar: Icon(_getCategoryIcon(item.category), size: 18),
                    ),
                    const SizedBox(width: 8),
                    Chip(
                      label: Text(item.unit.getName(locale)),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // SKU والباركود
                if (item.sku != null || item.barcode != null)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        children: [
                          if (item.sku != null)
                            _buildInfoRow(context, 'SKU', item.sku!),
                          if (item.sku != null && item.barcode != null)
                            const Divider(height: 16),
                          if (item.barcode != null)
                            _buildInfoRow(context, 'الباركود', item.barcode!),
                        ],
                      ),
                    ),
                  ),

                const SizedBox(height: 16),

                // حالة المخزون
                Text(
                  'حالة المخزون',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),

                // الكمية الحالية
                Row(
                  children: [
                    Expanded(
                      child: _buildStatCard(
                        context,
                        'المخزون الحالي',
                        '${item.currentStock.toStringAsFixed(1)} ${item.unit.getName(locale)}',
                        _getStockColor(item),
                        Icons.inventory,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildStatCard(
                        context,
                        'الحد الأدنى',
                        '${item.reorderLevel.toStringAsFixed(1)} ${item.unit.getName(locale)}',
                        Colors.orange,
                        Icons.warning,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // مؤشر المخزون
                StockLevelIndicator(
                  current: item.currentStock,
                  reorderLevel: item.reorderLevel,
                  maxCapacity: item.maxCapacity,
                  showLabels: true,
                  height: 32,
                ),

                const SizedBox(height: 16),

                // حالة المخزون
                _buildStatusBadge(context, item),

                const SizedBox(height: 24),

                // معلومات إضافية
                if (item.description != null ||
                    item.supplierId != null ||
                    item.batchNumber != null ||
                    item.expiryDate != null) ...[
                  Text(
                    'معلومات إضافية',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 12),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        children: [
                          if (item.description != null) ...[
                            _buildInfoRow(
                              context,
                              'الوصف',
                              item.getDescription(locale) ?? '',
                            ),
                            const Divider(height: 16),
                          ],
                          if (item.supplierName != null) ...[
                            _buildInfoRow(context, 'المورد', item.supplierName!),
                            const Divider(height: 16),
                          ],
                          if (item.batchNumber != null) ...[
                            _buildInfoRow(context, 'رقم الدفعة', item.batchNumber!),
                            const Divider(height: 16),
                          ],
                          if (item.lotNumber != null) ...[
                            _buildInfoRow(context, 'رقم اللوت', item.lotNumber!),
                            const Divider(height: 16),
                          ],
                          if (item.expiryDate != null) ...[
                            _buildInfoRow(
                              context,
                              'تاريخ الانتهاء',
                              DateFormat('dd/MM/yyyy').format(item.expiryDate!),
                            ),
                            const Divider(height: 16),
                          ],
                          if (item.unitPrice != null)
                            _buildInfoRow(
                              context,
                              'السعر',
                              '${item.unitPrice!.toStringAsFixed(2)} ريال',
                            ),
                        ],
                      ),
                    ),
                  ),
                ],

                const SizedBox(height: 24),

                // إجراءات سريعة
                Text(
                  'إجراءات سريعة',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _navigateToStockMovement(
                          context,
                          item,
                          MovementType.stockIn,
                        ),
                        icon: const Icon(Icons.add),
                        label: const Text('إدخال'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _navigateToStockMovement(
                          context,
                          item,
                          MovementType.stockOut,
                        ),
                        icon: const Icon(Icons.remove),
                        label: const Text('إخراج'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _navigateToStockMovement(
                      context,
                      item,
                      MovementType.fieldApplication,
                    ),
                    icon: const Icon(Icons.agriculture),
                    label: const Text('تطبيق على الحقل'),
                  ),
                ),

                const SizedBox(height: 24),

                // سجل الحركات
                Text(
                  'سجل الحركات',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
              ],
            ),
          ),

          // قائمة الحركات
          movementsAsync.when(
            data: (movements) {
              if (movements.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.all(32),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(
                          Icons.history,
                          size: 48,
                          color: Colors.grey.shade300,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'لا توجد حركات',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                  ),
                );
              }

              return ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: movements.length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  return MovementTile(movement: movements[index]);
                },
              );
            },
            loading: () => const Padding(
              padding: EdgeInsets.all(32),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (error, stack) => Padding(
              padding: const EdgeInsets.all(32),
              child: Center(
                child: Text('فشل في تحميل السجل: $error'),
              ),
            ),
          ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildImagePlaceholder(BuildContext context, InventoryItem item) {
    return Container(
      height: 200,
      color: Colors.grey.shade100,
      child: Center(
        child: Icon(
          _getCategoryIcon(item.category),
          size: 64,
          color: Theme.of(context).primaryColor.withOpacity(0.3),
        ),
      ),
    );
  }

  Widget _buildInfoRow(BuildContext context, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 100,
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey.shade600,
                ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String label,
    String value,
    Color color,
    IconData icon,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(BuildContext context, InventoryItem item) {
    final locale = Localizations.localeOf(context).languageCode;
    final status = item.stockStatus;
    final color = _getStockColor(item);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(
            _getStatusIcon(status),
            color: color,
          ),
          const SizedBox(width: 12),
          Text(
            status.getName(locale),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getStatusIcon(StockStatus status) {
    switch (status) {
      case StockStatus.good:
        return Icons.check_circle;
      case StockStatus.low:
        return Icons.warning;
      case StockStatus.critical:
        return Icons.error;
      case StockStatus.outOfStock:
        return Icons.remove_circle;
      case StockStatus.expiring:
        return Icons.event_busy;
    }
  }

  Color _getStockColor(InventoryItem item) {
    if (item.isOutOfStock) return Colors.red.shade700;
    if (item.isCritical) return Colors.red.shade600;
    if (item.isLowStock) return Colors.orange.shade600;
    return Colors.green.shade600;
  }

  IconData _getCategoryIcon(ItemCategory category) {
    switch (category) {
      case ItemCategory.fertilizer:
        return Icons.grass;
      case ItemCategory.pesticide:
        return Icons.bug_report;
      case ItemCategory.seed:
        return Icons.eco;
      case ItemCategory.equipment:
        return Icons.build;
      case ItemCategory.tool:
        return Icons.handyman;
      case ItemCategory.chemical:
        return Icons.science;
      case ItemCategory.feed:
        return Icons.pets;
      case ItemCategory.spare:
        return Icons.settings;
      case ItemCategory.other:
        return Icons.inventory_2;
    }
  }

  void _navigateToStockMovement(
    BuildContext context,
    InventoryItem item,
    MovementType movementType,
  ) {
    // Navigate to stock movement screen
    // Navigator.push(
    //   context,
    //   MaterialPageRoute(
    //     builder: (_) => StockMovementScreen(
    //       item: item,
    //       movementType: movementType,
    //     ),
    //   ),
    // );
  }

  void _showDeleteConfirmation(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف العنصر'),
        content: const Text('هل أنت متأكد من حذف هذا العنصر؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final controller = ref.read(inventoryControllerProvider.notifier);
              final success = await controller.deleteItem(itemId);
              if (context.mounted) {
                if (success) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('تم حذف العنصر بنجاح')),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('فشل في حذف العنصر')),
                  );
                }
              }
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }
}
