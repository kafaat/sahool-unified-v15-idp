/// Schedule Maintenance Screen - شاشة جدولة الصيانة
/// Screen to schedule maintenance for equipment
library;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../state/equipment_providers.dart';

/// Schedule Maintenance Screen
class ScheduleMaintenanceScreen extends ConsumerStatefulWidget {
  final String equipmentId;

  const ScheduleMaintenanceScreen({
    super.key,
    required this.equipmentId,
  });

  @override
  ConsumerState<ScheduleMaintenanceScreen> createState() =>
      _ScheduleMaintenanceScreenState();
}

class _ScheduleMaintenanceScreenState
    extends ConsumerState<ScheduleMaintenanceScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _descriptionArController = TextEditingController();
  final _notesController = TextEditingController();
  final _hoursController = TextEditingController();

  MaintenanceType _maintenanceType = MaintenanceType.generalService;
  MaintenancePriority _priority = MaintenancePriority.medium;
  DateTime _scheduledDate = DateTime.now().add(const Duration(days: 7));
  bool _isRecurring = false;
  int? _recurringIntervalDays;
  int? _recurringIntervalHours;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _descriptionController.dispose();
    _descriptionArController.dispose();
    _notesController.dispose();
    _hoursController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _scheduledDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: const Locale('ar'),
    );
    if (picked != null) {
      setState(() => _scheduledDate = picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: const Text('جدولة صيانة'),
        backgroundColor: SahoolColors.harvestGold,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Maintenance type
              const Text(
                'نوع الصيانة *',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: DropdownButtonFormField<MaintenanceType>(
                  value: _maintenanceType,
                  decoration: const InputDecoration(
                    border: InputBorder.none,
                    prefixIcon: Icon(Icons.build),
                  ),
                  items: MaintenanceType.values.map((type) {
                    return DropdownMenuItem(
                      value: type,
                      child: Text(type.nameAr),
                    );
                  }).toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _maintenanceType = value);
                    }
                  },
                ),
              ),
              const SizedBox(height: 20),

              // Priority
              const Text(
                'الأولوية *',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: MaintenancePriority.values.map((priority) {
                  final isSelected = _priority == priority;
                  return ChoiceChip(
                    label: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _getPriorityIcon(priority),
                          size: 16,
                          color: isSelected
                              ? _getPriorityColor(priority)
                              : Colors.grey,
                        ),
                        const SizedBox(width: 4),
                        Text(priority.nameAr),
                      ],
                    ),
                    selected: isSelected,
                    onSelected: (selected) {
                      if (selected) {
                        setState(() => _priority = priority);
                      }
                    },
                    selectedColor: _getPriorityColor(priority).withValues(alpha: 0.2),
                    labelStyle: TextStyle(
                      color: isSelected
                          ? _getPriorityColor(priority)
                          : Colors.grey[700],
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 20),

              // Scheduled date
              const Text(
                'تاريخ الصيانة *',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 12),
              InkWell(
                onTap: _selectDate,
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.calendar_today,
                          color: SahoolColors.harvestGold),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${_scheduledDate.day}/${_scheduledDate.month}/${_scheduledDate.year}',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            Text(
                              _getDaysUntilText(),
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.arrow_drop_down, color: Colors.grey),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Schedule at hours
              TextFormField(
                controller: _hoursController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'عند وصول ساعات التشغيل (اختياري)',
                  hintText: 'مثال: 500',
                  prefixIcon: const Icon(Icons.timer),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Description
              TextFormField(
                controller: _descriptionController,
                maxLines: 2,
                decoration: InputDecoration(
                  labelText: 'وصف الصيانة (إنجليزي)',
                  hintText: 'مثال: Regular oil change and filter replacement',
                  prefixIcon: const Icon(Icons.description),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _descriptionArController,
                maxLines: 2,
                decoration: InputDecoration(
                  labelText: 'وصف الصيانة (عربي) *',
                  hintText: 'مثال: تغيير زيت دوري واستبدال الفلتر',
                  prefixIcon: const Icon(Icons.description),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال وصف الصيانة';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),

              // Recurring toggle
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.repeat, color: SahoolColors.forestGreen),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Text(
                            'صيانة دورية',
                            style: TextStyle(fontWeight: FontWeight.w500),
                          ),
                        ),
                        Switch(
                          value: _isRecurring,
                          onChanged: (value) {
                            setState(() => _isRecurring = value);
                          },
                          activeColor: SahoolColors.forestGreen,
                        ),
                      ],
                    ),
                    if (_isRecurring) ...[
                      const Divider(),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'كل (أيام)',
                                  style: TextStyle(fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                DropdownButton<int>(
                                  value: _recurringIntervalDays,
                                  hint: const Text('اختر'),
                                  isExpanded: true,
                                  items: [7, 14, 30, 60, 90, 180, 365]
                                      .map((days) => DropdownMenuItem(
                                            value: days,
                                            child: Text('$days يوم'),
                                          ))
                                      .toList(),
                                  onChanged: (value) {
                                    setState(() {
                                      _recurringIntervalDays = value;
                                      _recurringIntervalHours = null;
                                    });
                                  },
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 16),
                          const Text('أو'),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'كل (ساعات)',
                                  style: TextStyle(fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                DropdownButton<int>(
                                  value: _recurringIntervalHours,
                                  hint: const Text('اختر'),
                                  isExpanded: true,
                                  items: [50, 100, 250, 500, 1000]
                                      .map((hours) => DropdownMenuItem(
                                            value: hours,
                                            child: Text('$hours ساعة'),
                                          ))
                                      .toList(),
                                  onChanged: (value) {
                                    setState(() {
                                      _recurringIntervalHours = value;
                                      _recurringIntervalDays = null;
                                    });
                                  },
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Notes
              TextFormField(
                controller: _notesController,
                maxLines: 3,
                decoration: InputDecoration(
                  labelText: 'ملاحظات إضافية',
                  hintText: 'أي ملاحظات...',
                  prefixIcon: const Icon(Icons.note),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Submit button
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : _submitForm,
                  icon: _isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.schedule),
                  label: Text(_isSubmitting ? 'جاري الجدولة...' : 'جدولة الصيانة'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: SahoolColors.harvestGold,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  String _getDaysUntilText() {
    final days = _scheduledDate.difference(DateTime.now()).inDays;
    if (days == 0) return 'اليوم';
    if (days == 1) return 'غدا';
    if (days < 7) return 'بعد $days أيام';
    if (days < 30) return 'بعد ${(days / 7).floor()} أسابيع';
    return 'بعد ${(days / 30).floor()} شهر';
  }

  IconData _getPriorityIcon(MaintenancePriority priority) {
    switch (priority) {
      case MaintenancePriority.low:
        return Icons.keyboard_arrow_down;
      case MaintenancePriority.medium:
        return Icons.remove;
      case MaintenancePriority.high:
        return Icons.keyboard_arrow_up;
      case MaintenancePriority.critical:
        return Icons.priority_high;
    }
  }

  Color _getPriorityColor(MaintenancePriority priority) {
    switch (priority) {
      case MaintenancePriority.low:
        return Colors.green;
      case MaintenancePriority.medium:
        return SahoolColors.harvestGold;
      case MaintenancePriority.high:
        return Colors.orange;
      case MaintenancePriority.critical:
        return SahoolColors.danger;
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final controller = ref.read(equipmentControllerProvider.notifier);
      final success = await controller.scheduleMaintenance(
        widget.equipmentId,
        maintenanceType: _maintenanceType,
        priority: _priority,
        description: _descriptionController.text.isNotEmpty
            ? _descriptionController.text
            : _descriptionArController.text,
        descriptionAr: _descriptionArController.text,
        scheduledDate: _scheduledDate,
        scheduledAtHours: double.tryParse(_hoursController.text),
        isRecurring: _isRecurring,
        recurringIntervalDays: _recurringIntervalDays,
        recurringIntervalHours: _recurringIntervalHours,
      );

      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم جدولة الصيانة بنجاح'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('فشل في جدولة الصيانة'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
}
