/// Inventory Card Widget - بطاقة عنصر المخزون
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../data/inventory_models.dart';
import 'stock_level_indicator.dart';

/// بطاقة عرض عنصر المخزون
class InventoryCard extends StatelessWidget {
  final InventoryItem item;
  final VoidCallback? onTap;
  final bool isGridView;

  const InventoryCard({
    super.key,
    required this.item,
    this.onTap,
    this.isGridView = false,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;

    if (isGridView) {
      return _buildGridCard(context, locale);
    } else {
      return _buildListCard(context, locale);
    }
  }

  Widget _buildGridCard(BuildContext context, String locale) {
    return Card(
      elevation: 2,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // الصورة أو الأيقونة
            AspectRatio(
              aspectRatio: 1,
              child: _buildImageSection(context),
            ),
            // المعلومات
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // الاسم
                    Text(
                      item.getDisplayName(locale),
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    // الفئة
                    Row(
                      children: [
                        Icon(
                          _getCategoryIcon(item.category),
                          size: 14,
                          color: Colors.grey.shade600,
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            item.category.getName(locale),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Colors.grey.shade600,
                                ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const Spacer(),
                    // الكمية
                    Row(
                      children: [
                        Text(
                          item.currentStock.toStringAsFixed(1),
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: _getStockColor(item),
                              ),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          item.unit.getName(locale),
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.grey.shade600,
                              ),
                        ),
                        const Spacer(),
                        StockStatusIndicator(
                          current: item.currentStock,
                          reorderLevel: item.reorderLevel,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // الشارات
                    _buildBadges(context, locale),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListCard(BuildContext context, String locale) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // الصورة أو الأيقونة
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  color: Colors.grey.shade100,
                ),
                child: _buildImageSection(context),
              ),
              const SizedBox(width: 12),
              // المعلومات
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // الاسم والحالة
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item.getDisplayName(locale),
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 8),
                        StockStatusIndicator(
                          current: item.currentStock,
                          reorderLevel: item.reorderLevel,
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    // الفئة
                    Row(
                      children: [
                        Icon(
                          _getCategoryIcon(item.category),
                          size: 14,
                          color: Colors.grey.shade600,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          item.category.getName(locale),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.grey.shade600,
                              ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // مؤشر المخزون
                    StockLevelIndicator(
                      current: item.currentStock,
                      reorderLevel: item.reorderLevel,
                      maxCapacity: item.maxCapacity,
                      height: 8,
                      showPercentage: false,
                    ),
                    const SizedBox(height: 8),
                    // الكمية والشارات
                    Row(
                      children: [
                        Text(
                          '${item.currentStock.toStringAsFixed(1)} ${item.unit.getName(locale)}',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: _getStockColor(item),
                              ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(child: _buildBadges(context, locale)),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageSection(BuildContext context) {
    if (item.imageUrl != null && item.imageUrl!.isNotEmpty) {
      return Image.network(
        item.imageUrl!,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => _buildIconPlaceholder(context),
      );
    }
    return _buildIconPlaceholder(context);
  }

  Widget _buildIconPlaceholder(BuildContext context) {
    return Center(
      child: Icon(
        _getCategoryIcon(item.category),
        size: isGridView ? 48 : 40,
        color: Theme.of(context).primaryColor.withOpacity(0.3),
      ),
    );
  }

  Widget _buildBadges(BuildContext context, String locale) {
    final badges = <Widget>[];

    if (item.isLowStock) {
      badges.add(_buildBadge(
        context,
        item.isCritical ? 'حرج' : 'منخفض',
        item.isCritical ? Colors.red : Colors.orange,
      ));
    }

    if (item.isExpiringSoon) {
      badges.add(_buildBadge(
        context,
        'قرب الانتهاء',
        Colors.orange.shade700,
      ));
    }

    if (item.lastStockIn != null) {
      final lastIn = item.lastStockIn!;
      final daysAgo = DateTime.now().difference(lastIn).inDays;
      if (daysAgo == 0) {
        badges.add(_buildBadge(
          context,
          'وارد اليوم',
          Colors.green,
        ));
      }
    }

    return Wrap(
      spacing: 4,
      runSpacing: 4,
      children: badges,
    );
  }

  Widget _buildBadge(BuildContext context, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: color.shade800,
        ),
      ),
    );
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
}
