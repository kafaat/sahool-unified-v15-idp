/// Category Filter Widget - فلتر الفئات
library;

import 'package:flutter/material.dart';

import '../data/inventory_models.dart';

/// شريحة فلتر الفئات
class CategoryFilter extends StatelessWidget {
  final ItemCategory? selectedCategory;
  final ValueChanged<ItemCategory?> onCategoryChanged;

  const CategoryFilter({
    super.key,
    this.selectedCategory,
    required this.onCategoryChanged,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;

    return SizedBox(
      height: 50,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          // الكل
          Padding(
            padding: const EdgeInsets.only(left: 8),
            child: FilterChip(
              label: const Text('الكل'),
              selected: selectedCategory == null,
              onSelected: (_) => onCategoryChanged(null),
              backgroundColor: Colors.grey.shade100,
              selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
            ),
          ),
          // الفئات
          ...ItemCategory.values.map((category) {
            return Padding(
              padding: const EdgeInsets.only(left: 8),
              child: FilterChip(
                label: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _getCategoryIcon(category),
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(category.getName(locale)),
                  ],
                ),
                selected: selectedCategory == category,
                onSelected: (_) => onCategoryChanged(category),
                backgroundColor: Colors.grey.shade100,
                selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
              ),
            );
          }),
        ],
      ),
    );
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
