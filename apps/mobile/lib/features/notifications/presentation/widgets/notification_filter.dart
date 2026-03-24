/// SAHOOL Notification Filter Widget
/// عنصر فلترة الإشعارات
///
/// Provides filtering options for notifications by:
/// - Category
/// - Status (read/unread)
/// - Priority
/// - Date range
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../domain/models/notification.dart';
import '../../domain/models/notification_category.dart';

/// Filter state model
class NotificationFilterState {
  final Set<NotificationCategory> categories;
  final Set<NotificationStatus> statuses;
  final Set<NotificationPriority> priorities;
  final DateTime? fromDate;
  final DateTime? toDate;
  final String? searchQuery;

  const NotificationFilterState({
    this.categories = const {},
    this.statuses = const {},
    this.priorities = const {},
    this.fromDate,
    this.toDate,
    this.searchQuery,
  });

  bool get isEmpty =>
      categories.isEmpty &&
      statuses.isEmpty &&
      priorities.isEmpty &&
      fromDate == null &&
      toDate == null &&
      (searchQuery == null || searchQuery!.isEmpty);

  int get activeFilterCount {
    int count = 0;
    if (categories.isNotEmpty) count++;
    if (statuses.isNotEmpty) count++;
    if (priorities.isNotEmpty) count++;
    if (fromDate != null || toDate != null) count++;
    if (searchQuery != null && searchQuery!.isNotEmpty) count++;
    return count;
  }

  NotificationFilterState copyWith({
    Set<NotificationCategory>? categories,
    Set<NotificationStatus>? statuses,
    Set<NotificationPriority>? priorities,
    DateTime? fromDate,
    DateTime? toDate,
    String? searchQuery,
    bool clearFromDate = false,
    bool clearToDate = false,
    bool clearSearch = false,
  }) {
    return NotificationFilterState(
      categories: categories ?? this.categories,
      statuses: statuses ?? this.statuses,
      priorities: priorities ?? this.priorities,
      fromDate: clearFromDate ? null : (fromDate ?? this.fromDate),
      toDate: clearToDate ? null : (toDate ?? this.toDate),
      searchQuery: clearSearch ? null : (searchQuery ?? this.searchQuery),
    );
  }

  NotificationFilterState clear() {
    return const NotificationFilterState();
  }
}

/// Filter bar widget
class NotificationFilterBar extends StatelessWidget {
  final NotificationFilterState filter;
  final ValueChanged<NotificationFilterState> onFilterChanged;

  const NotificationFilterBar({
    super.key,
    required this.filter,
    required this.onFilterChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        border: Border(
          bottom: BorderSide(color: Colors.grey.shade300),
        ),
      ),
      child: Row(
        children: [
          // Filter button
          _FilterChipButton(
            label: 'فلترة',
            icon: Icons.filter_list,
            count: filter.activeFilterCount,
            onTap: () => _showFilterSheet(context),
          ),

          const SizedBox(width: 8),

          // Quick filters
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  // Unread only
                  _QuickFilterChip(
                    label: 'غير مقروء',
                    isSelected: filter.statuses
                        .contains(NotificationStatus.unread),
                    onTap: () {
                      final newStatuses = Set<NotificationStatus>.from(
                        filter.statuses,
                      );
                      if (newStatuses.contains(NotificationStatus.unread)) {
                        newStatuses.remove(NotificationStatus.unread);
                      } else {
                        newStatuses.add(NotificationStatus.unread);
                      }
                      onFilterChanged(filter.copyWith(statuses: newStatuses));
                    },
                  ),

                  const SizedBox(width: 8),

                  // High priority only
                  _QuickFilterChip(
                    label: 'مهم',
                    icon: Icons.priority_high,
                    color: Colors.red,
                    isSelected: filter.priorities
                            .contains(NotificationPriority.high) ||
                        filter.priorities
                            .contains(NotificationPriority.critical),
                    onTap: () {
                      final newPriorities = Set<NotificationPriority>.from(
                        filter.priorities,
                      );
                      if (newPriorities.contains(NotificationPriority.high) ||
                          newPriorities
                              .contains(NotificationPriority.critical)) {
                        newPriorities.remove(NotificationPriority.high);
                        newPriorities.remove(NotificationPriority.critical);
                      } else {
                        newPriorities.add(NotificationPriority.high);
                        newPriorities.add(NotificationPriority.critical);
                      }
                      onFilterChanged(
                        filter.copyWith(priorities: newPriorities),
                      );
                    },
                  ),

                  // Category filters
                  ...NotificationCategory.values.take(4).map((category) {
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: _QuickFilterChip(
                        label: category.labelAr,
                        icon: category.icon,
                        color: category.color,
                        isSelected: filter.categories.contains(category),
                        onTap: () {
                          final newCategories =
                              Set<NotificationCategory>.from(filter.categories);
                          if (newCategories.contains(category)) {
                            newCategories.remove(category);
                          } else {
                            newCategories.add(category);
                          }
                          onFilterChanged(
                            filter.copyWith(categories: newCategories),
                          );
                        },
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),

          // Clear filters
          if (!filter.isEmpty)
            IconButton(
              icon: const Icon(Icons.clear, size: 20),
              tooltip: 'مسح الفلاتر',
              onPressed: () => onFilterChanged(filter.clear()),
            ),
        ],
      ),
    );
  }

  void _showFilterSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => NotificationFilterSheet(
        filter: filter,
        onApply: (newFilter) {
          Navigator.pop(context);
          onFilterChanged(newFilter);
        },
      ),
    );
  }
}

class _FilterChipButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final int count;
  final VoidCallback onTap;

  const _FilterChipButton({
    required this.label,
    required this.icon,
    required this.count,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: count > 0 ? Theme.of(context).primaryColor : Colors.white,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            border: Border.all(
              color: count > 0
                  ? Theme.of(context).primaryColor
                  : Colors.grey.shade400,
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 18,
                color: count > 0 ? Colors.white : Colors.grey.shade600,
              ),
              const SizedBox(width: 4),
              Text(
                label,
                style: TextStyle(
                  color: count > 0 ? Colors.white : Colors.grey.shade600,
                  fontSize: 13,
                ),
              ),
              if (count > 0) ...[
                const SizedBox(width: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    count.toString(),
                    style: TextStyle(
                      color: Theme.of(context).primaryColor,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _QuickFilterChip extends StatelessWidget {
  final String label;
  final IconData? icon;
  final Color? color;
  final bool isSelected;
  final VoidCallback onTap;

  const _QuickFilterChip({
    required this.label,
    this.icon,
    this.color,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final chipColor = color ?? Theme.of(context).primaryColor;

    return Material(
      color: isSelected ? chipColor.withValues(alpha: 0.15) : Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            border: Border.all(
              color: isSelected ? chipColor : Colors.grey.shade400,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(
                  icon,
                  size: 14,
                  color: isSelected ? chipColor : Colors.grey.shade600,
                ),
                const SizedBox(width: 4),
              ],
              Text(
                label,
                style: TextStyle(
                  color: isSelected ? chipColor : Colors.grey.shade600,
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Full filter sheet
class NotificationFilterSheet extends StatefulWidget {
  final NotificationFilterState filter;
  final ValueChanged<NotificationFilterState> onApply;

  const NotificationFilterSheet({
    super.key,
    required this.filter,
    required this.onApply,
  });

  @override
  State<NotificationFilterSheet> createState() =>
      _NotificationFilterSheetState();
}

class _NotificationFilterSheetState extends State<NotificationFilterSheet> {
  late NotificationFilterState _filter;

  @override
  void initState() {
    super.initState();
    _filter = widget.filter;
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) {
        return Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12, bottom: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _filter = const NotificationFilterState();
                      });
                    },
                    child: const Text('مسح الكل'),
                  ),
                  const Text(
                    'فلترة الإشعارات',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  TextButton(
                    onPressed: () => widget.onApply(_filter),
                    child: const Text('تطبيق'),
                  ),
                ],
              ),
            ),

            const Divider(),

            // Filter options
            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.all(16),
                children: [
                  // Categories
                  _buildSectionTitle('الفئات'),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: NotificationCategory.values.map((category) {
                      final isSelected = _filter.categories.contains(category);
                      return FilterChip(
                        label: Text(category.labelAr),
                        avatar: Icon(category.icon, size: 18),
                        selected: isSelected,
                        selectedColor: category.lightColor,
                        checkmarkColor: category.color,
                        onSelected: (selected) {
                          setState(() {
                            final newCategories = Set<NotificationCategory>.from(
                              _filter.categories,
                            );
                            if (selected) {
                              newCategories.add(category);
                            } else {
                              newCategories.remove(category);
                            }
                            _filter = _filter.copyWith(categories: newCategories);
                          });
                        },
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 24),

                  // Status
                  _buildSectionTitle('الحالة'),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      FilterChip(
                        label: const Text('غير مقروء'),
                        selected: _filter.statuses
                            .contains(NotificationStatus.unread),
                        onSelected: (selected) => _toggleStatus(
                          NotificationStatus.unread,
                          selected,
                        ),
                      ),
                      FilterChip(
                        label: const Text('مقروء'),
                        selected: _filter.statuses
                            .contains(NotificationStatus.read),
                        onSelected: (selected) => _toggleStatus(
                          NotificationStatus.read,
                          selected,
                        ),
                      ),
                      FilterChip(
                        label: const Text('مؤجل'),
                        selected: _filter.statuses
                            .contains(NotificationStatus.snoozed),
                        onSelected: (selected) => _toggleStatus(
                          NotificationStatus.snoozed,
                          selected,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Priority
                  _buildSectionTitle('الأولوية'),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: NotificationPriority.values.map((priority) {
                      final isSelected = _filter.priorities.contains(priority);
                      return FilterChip(
                        label: Text(priority.labelAr),
                        selected: isSelected,
                        selectedColor: priority.color.withValues(alpha: 0.2),
                        checkmarkColor: priority.color,
                        onSelected: (selected) {
                          setState(() {
                            final newPriorities =
                                Set<NotificationPriority>.from(
                              _filter.priorities,
                            );
                            if (selected) {
                              newPriorities.add(priority);
                            } else {
                              newPriorities.remove(priority);
                            }
                            _filter = _filter.copyWith(priorities: newPriorities);
                          });
                        },
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 24),

                  // Date range
                  _buildSectionTitle('التاريخ'),
                  Row(
                    children: [
                      Expanded(
                        child: _DatePickerField(
                          label: 'من',
                          date: _filter.fromDate,
                          onDateSelected: (date) {
                            setState(() {
                              _filter = _filter.copyWith(fromDate: date);
                            });
                          },
                          onClear: () {
                            setState(() {
                              _filter = _filter.copyWith(clearFromDate: true);
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _DatePickerField(
                          label: 'إلى',
                          date: _filter.toDate,
                          onDateSelected: (date) {
                            setState(() {
                              _filter = _filter.copyWith(toDate: date);
                            });
                          },
                          onClear: () {
                            setState(() {
                              _filter = _filter.copyWith(clearToDate: true);
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  void _toggleStatus(NotificationStatus status, bool selected) {
    setState(() {
      final newStatuses = Set<NotificationStatus>.from(_filter.statuses);
      if (selected) {
        newStatuses.add(status);
      } else {
        newStatuses.remove(status);
      }
      _filter = _filter.copyWith(statuses: newStatuses);
    });
  }
}

class _DatePickerField extends StatelessWidget {
  final String label;
  final DateTime? date;
  final ValueChanged<DateTime> onDateSelected;
  final VoidCallback onClear;

  const _DatePickerField({
    required this.label,
    required this.date,
    required this.onDateSelected,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () async {
        final selected = await showDatePicker(
          context: context,
          initialDate: date ?? DateTime.now(),
          firstDate: DateTime.now().subtract(const Duration(days: 365)),
          lastDate: DateTime.now(),
        );
        if (selected != null) {
          onDateSelected(selected);
        }
      },
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
          suffixIcon: date != null
              ? IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: onClear,
                )
              : const Icon(Icons.calendar_today, size: 18),
        ),
        child: Text(
          date != null
              ? DateFormat('dd/MM/yyyy').format(date!)
              : 'اختر تاريخ',
          style: TextStyle(
            color: date != null ? null : Colors.grey,
          ),
        ),
      ),
    );
  }
}
