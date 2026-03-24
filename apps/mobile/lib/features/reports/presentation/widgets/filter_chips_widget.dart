/// Filter Chips Widget - ودجت رقائق التصفية
/// Reusable filter chips for field and farm selection
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Filter type enum
enum FilterType {
  field,
  farm,
  crop,
  task,
}

/// Filter Chips Widget
/// ودجت رقائق التصفية
class FilterChipsWidget extends ConsumerStatefulWidget {
  final List<String> selectedIds;
  final FilterType filterType;
  final Function(List<String>) onSelectionChanged;
  final int maxSelection;
  final bool allowMultiple;

  const FilterChipsWidget({
    super.key,
    required this.selectedIds,
    required this.filterType,
    required this.onSelectionChanged,
    this.maxSelection = 10,
    this.allowMultiple = true,
  });

  @override
  ConsumerState<FilterChipsWidget> createState() => _FilterChipsWidgetState();
}

class _FilterChipsWidgetState extends ConsumerState<FilterChipsWidget> {
  late List<String> _selectedIds;
  bool _isExpanded = false;

  // Mock data - in production, this would come from providers
  List<FilterItem> get _items {
    switch (widget.filterType) {
      case FilterType.field:
        return [
          const FilterItem(id: 'field_1', name: 'Field 1', nameAr: 'حقل القمح الشمالي'),
          const FilterItem(id: 'field_2', name: 'Field 2', nameAr: 'حقل الذرة الغربي'),
          const FilterItem(id: 'field_3', name: 'Field 3', nameAr: 'حقل الشعير'),
          const FilterItem(id: 'field_4', name: 'Field 4', nameAr: 'حقل البرسيم'),
          const FilterItem(id: 'field_5', name: 'Field 5', nameAr: 'حقل الخضار'),
        ];
      case FilterType.farm:
        return [
          const FilterItem(id: 'farm_1', name: 'Farm 1', nameAr: 'مزرعة الراشدي'),
          const FilterItem(id: 'farm_2', name: 'Farm 2', nameAr: 'مزرعة الخضراء'),
        ];
      case FilterType.crop:
        return [
          const FilterItem(id: 'wheat', name: 'Wheat', nameAr: 'قمح'),
          const FilterItem(id: 'barley', name: 'Barley', nameAr: 'شعير'),
          const FilterItem(id: 'corn', name: 'Corn', nameAr: 'ذرة'),
          const FilterItem(id: 'alfalfa', name: 'Alfalfa', nameAr: 'برسيم'),
          const FilterItem(id: 'tomato', name: 'Tomato', nameAr: 'طماطم'),
        ];
      case FilterType.task:
        return [
          const FilterItem(id: 'irrigation', name: 'Irrigation', nameAr: 'الري'),
          const FilterItem(id: 'fertilization', name: 'Fertilization', nameAr: 'التسميد'),
          const FilterItem(id: 'spraying', name: 'Spraying', nameAr: 'الرش'),
          const FilterItem(id: 'inspection', name: 'Inspection', nameAr: 'التفقد'),
          const FilterItem(id: 'harvest', name: 'Harvest', nameAr: 'الحصاد'),
        ];
    }
  }

  @override
  void initState() {
    super.initState();
    _selectedIds = List.from(widget.selectedIds);
  }

  @override
  void didUpdateWidget(FilterChipsWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedIds != widget.selectedIds) {
      _selectedIds = List.from(widget.selectedIds);
    }
  }

  void _toggleSelection(String id) {
    setState(() {
      if (_selectedIds.contains(id)) {
        _selectedIds.remove(id);
      } else {
        if (!widget.allowMultiple) {
          _selectedIds.clear();
        }
        if (_selectedIds.length < widget.maxSelection) {
          _selectedIds.add(id);
        }
      }
    });
    widget.onSelectionChanged(_selectedIds);
  }

  void _selectAll() {
    setState(() {
      _selectedIds = _items.map((i) => i.id).take(widget.maxSelection).toList();
    });
    widget.onSelectionChanged(_selectedIds);
  }

  void _clearAll() {
    setState(() {
      _selectedIds.clear();
    });
    widget.onSelectionChanged(_selectedIds);
  }

  @override
  Widget build(BuildContext context) {
    final visibleItems = _isExpanded ? _items : _items.take(4).toList();
    final hasMore = _items.length > 4;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Quick actions
        if (widget.allowMultiple)
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                onPressed: _selectedIds.isEmpty ? null : _clearAll,
                icon: const Icon(Icons.clear_all, size: 16),
                label: const Text('مسح'),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.grey,
                  textStyle: const TextStyle(fontSize: 12),
                ),
              ),
              TextButton.icon(
                onPressed: _selectedIds.length == _items.length ? null : _selectAll,
                icon: const Icon(Icons.select_all, size: 16),
                label: const Text('تحديد الكل'),
                style: TextButton.styleFrom(
                  foregroundColor: SahoolColors.primary,
                  textStyle: const TextStyle(fontSize: 12),
                ),
              ),
            ],
          ),

        // Chips
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...visibleItems.map((item) => _buildChip(item)),
            if (hasMore && !_isExpanded)
              ActionChip(
                label: Text('+${_items.length - 4}'),
                avatar: const Icon(Icons.expand_more, size: 18),
                onPressed: () => setState(() => _isExpanded = true),
                backgroundColor: Colors.grey[200],
              ),
            if (hasMore && _isExpanded)
              ActionChip(
                label: const Text('إخفاء'),
                avatar: const Icon(Icons.expand_less, size: 18),
                onPressed: () => setState(() => _isExpanded = false),
                backgroundColor: Colors.grey[200],
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildChip(FilterItem item) {
    final isSelected = _selectedIds.contains(item.id);

    return FilterChip(
      label: Text(item.nameAr),
      selected: isSelected,
      onSelected: (_) => _toggleSelection(item.id),
      selectedColor: SahoolColors.primary.withValues(alpha: 0.2),
      checkmarkColor: SahoolColors.primary,
      backgroundColor: Colors.grey[100],
      labelStyle: TextStyle(
        color: isSelected ? SahoolColors.primary : Colors.grey[700],
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
      avatar: isSelected
          ? null
          : Icon(
              _getFilterIcon(),
              size: 16,
              color: Colors.grey[500],
            ),
    );
  }

  IconData _getFilterIcon() {
    switch (widget.filterType) {
      case FilterType.field:
        return Icons.landscape;
      case FilterType.farm:
        return Icons.home_work;
      case FilterType.crop:
        return Icons.grass;
      case FilterType.task:
        return Icons.task_alt;
    }
  }
}

/// Filter item model
class FilterItem {
  final String id;
  final String name;
  final String nameAr;

  const FilterItem({
    required this.id,
    required this.name,
    required this.nameAr,
  });
}

/// Compact Filter Chip Row
/// صف رقائق تصفية مضغوط
class CompactFilterChips extends StatelessWidget {
  final List<String> labels;
  final int? selectedIndex;
  final Function(int)? onSelected;

  const CompactFilterChips({
    super.key,
    required this.labels,
    this.selectedIndex,
    this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: labels.asMap().entries.map((entry) {
          final index = entry.key;
          final label = entry.value;
          final isSelected = selectedIndex == index;

          return Padding(
            padding: EdgeInsets.only(
              left: index == labels.length - 1 ? 0 : 8,
            ),
            child: ChoiceChip(
              label: Text(label),
              selected: isSelected,
              onSelected: onSelected != null ? (_) => onSelected!(index) : null,
              selectedColor: SahoolColors.primary.withValues(alpha: 0.2),
              labelStyle: TextStyle(
                color: isSelected ? SahoolColors.primary : Colors.grey[700],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 12,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
