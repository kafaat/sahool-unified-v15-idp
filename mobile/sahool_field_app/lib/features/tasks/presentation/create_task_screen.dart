import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/entities/task.dart';
import '../providers/tasks_provider.dart';

/// شاشة إنشاء مهمة جديدة
/// Create New Task Screen
class CreateTaskScreen extends ConsumerStatefulWidget {
  final String? fieldId;
  final String? fieldName;

  const CreateTaskScreen({
    super.key,
    this.fieldId,
    this.fieldName,
  });

  @override
  ConsumerState<CreateTaskScreen> createState() => _CreateTaskScreenState();
}

class _CreateTaskScreenState extends ConsumerState<CreateTaskScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _notesController = TextEditingController();

  TaskType _selectedType = TaskType.scouting;
  TaskPriority _selectedPriority = TaskPriority.medium;
  DateTime _dueDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _dueTime = const TimeOfDay(hour: 9, minute: 0);
  String? _selectedFieldId;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _selectedFieldId = widget.fieldId;
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مهمة جديدة'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            TextButton(
              onPressed: _isSubmitting ? null : _submitTask,
              child: const Text(
                'حفظ',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        body: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // نوع المهمة
                _buildSectionTitle('نوع المهمة'),
                _buildTaskTypeSelector(),
                const SizedBox(height: 24),

                // العنوان
                _buildSectionTitle('العنوان'),
                TextFormField(
                  controller: _titleController,
                  decoration: const InputDecoration(
                    hintText: 'أدخل عنوان المهمة',
                    prefixIcon: Icon(Icons.title),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'الرجاء إدخال عنوان المهمة';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),

                // الوصف
                _buildSectionTitle('الوصف'),
                TextFormField(
                  controller: _descriptionController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    hintText: 'أدخل وصف المهمة',
                    prefixIcon: Icon(Icons.description),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 24),

                // الحقل
                _buildSectionTitle('الحقل'),
                _buildFieldSelector(),
                const SizedBox(height: 24),

                // الأولوية
                _buildSectionTitle('الأولوية'),
                _buildPrioritySelector(),
                const SizedBox(height: 24),

                // تاريخ ووقت الاستحقاق
                _buildSectionTitle('موعد الاستحقاق'),
                Row(
                  children: [
                    Expanded(child: _buildDatePicker()),
                    const SizedBox(width: 12),
                    Expanded(child: _buildTimePicker()),
                  ],
                ),
                const SizedBox(height: 24),

                // ملاحظات إضافية
                _buildSectionTitle('ملاحظات إضافية'),
                TextFormField(
                  controller: _notesController,
                  maxLines: 2,
                  decoration: const InputDecoration(
                    hintText: 'ملاحظات إضافية (اختياري)',
                    prefixIcon: Icon(Icons.note_add),
                  ),
                ),
                const SizedBox(height: 32),

                // زر الإنشاء
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _isSubmitting ? null : _submitTask,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF367C2B),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    icon: _isSubmitting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.add_task),
                    label: Text(_isSubmitting ? 'جاري الحفظ...' : 'إنشاء المهمة'),
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 16,
          color: Color(0xFF367C2B),
        ),
      ),
    );
  }

  Widget _buildTaskTypeSelector() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: TaskType.values.map((type) {
        final isSelected = _selectedType == type;
        return ChoiceChip(
          label: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                _getTaskTypeIcon(type),
                size: 18,
                color: isSelected ? Colors.white : const Color(0xFF367C2B),
              ),
              const SizedBox(width: 6),
              Text(type.arabicLabel),
            ],
          ),
          selected: isSelected,
          onSelected: (selected) {
            if (selected) {
              setState(() => _selectedType = type);
            }
          },
          selectedColor: const Color(0xFF367C2B),
          labelStyle: TextStyle(
            color: isSelected ? Colors.white : Colors.black,
          ),
        );
      }).toList(),
    );
  }

  Widget _buildFieldSelector() {
    // مثال على قائمة الحقول
    final fields = [
      {'id': 'field1', 'name': 'حقل القمح الشمالي'},
      {'id': 'field2', 'name': 'حقل الذرة الغربي'},
      {'id': 'field3', 'name': 'حقل الشعير'},
      {'id': 'field4', 'name': 'حقل البرسيم'},
    ];

    return DropdownButtonFormField<String>(
      value: _selectedFieldId,
      decoration: const InputDecoration(
        prefixIcon: Icon(Icons.landscape),
        hintText: 'اختر الحقل',
      ),
      items: fields.map((field) {
        return DropdownMenuItem<String>(
          value: field['id'],
          child: Text(field['name']!),
        );
      }).toList(),
      onChanged: (value) {
        setState(() => _selectedFieldId = value);
      },
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'الرجاء اختيار الحقل';
        }
        return null;
      },
    );
  }

  Widget _buildPrioritySelector() {
    return Row(
      children: TaskPriority.values.map((priority) {
        final isSelected = _selectedPriority == priority;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: InkWell(
              onTap: () => setState(() => _selectedPriority = priority),
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: isSelected
                      ? _getPriorityColor(priority).withOpacity(0.2)
                      : Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isSelected
                        ? _getPriorityColor(priority)
                        : Colors.transparent,
                    width: 2,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      _getPriorityIcon(priority),
                      color: _getPriorityColor(priority),
                      size: 24,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      priority.arabicLabel,
                      style: TextStyle(
                        color: _getPriorityColor(priority),
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDatePicker() {
    return InkWell(
      onTap: () async {
        final picked = await showDatePicker(
          context: context,
          initialDate: _dueDate,
          firstDate: DateTime.now(),
          lastDate: DateTime.now().add(const Duration(days: 365)),
          locale: const Locale('ar'),
        );
        if (picked != null) {
          setState(() => _dueDate = picked);
        }
      },
      child: InputDecorator(
        decoration: const InputDecoration(
          prefixIcon: Icon(Icons.calendar_today),
        ),
        child: Text(
          '${_dueDate.day}/${_dueDate.month}/${_dueDate.year}',
        ),
      ),
    );
  }

  Widget _buildTimePicker() {
    return InkWell(
      onTap: () async {
        final picked = await showTimePicker(
          context: context,
          initialTime: _dueTime,
        );
        if (picked != null) {
          setState(() => _dueTime = picked);
        }
      },
      child: InputDecorator(
        decoration: const InputDecoration(
          prefixIcon: Icon(Icons.access_time),
        ),
        child: Text(
          '${_dueTime.hour.toString().padLeft(2, '0')}:${_dueTime.minute.toString().padLeft(2, '0')}',
        ),
      ),
    );
  }

  IconData _getTaskTypeIcon(TaskType type) {
    switch (type) {
      case TaskType.irrigation:
        return Icons.water_drop;
      case TaskType.fertilization:
        return Icons.eco;
      case TaskType.spraying:
        return Icons.pest_control;
      case TaskType.scouting:
        return Icons.search;
      case TaskType.harvesting:
        return Icons.agriculture;
      case TaskType.maintenance:
        return Icons.build;
      case TaskType.other:
        return Icons.more_horiz;
    }
  }

  Color _getPriorityColor(TaskPriority priority) {
    switch (priority) {
      case TaskPriority.urgent:
        return Colors.red;
      case TaskPriority.high:
        return Colors.orange;
      case TaskPriority.medium:
        return Colors.blue;
      case TaskPriority.low:
        return Colors.grey;
    }
  }

  IconData _getPriorityIcon(TaskPriority priority) {
    switch (priority) {
      case TaskPriority.urgent:
        return Icons.warning;
      case TaskPriority.high:
        return Icons.arrow_upward;
      case TaskPriority.medium:
        return Icons.remove;
      case TaskPriority.low:
        return Icons.arrow_downward;
    }
  }

  Future<void> _submitTask() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      // TODO: Implement actual task creation
      await Future.delayed(const Duration(seconds: 1));

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم إنشاء المهمة بنجاح'),
            backgroundColor: Color(0xFF367C2B),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل إنشاء المهمة: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
}

/// أنواع المهام
enum TaskType {
  irrigation,
  fertilization,
  spraying,
  scouting,
  harvesting,
  maintenance,
  other;

  String get arabicLabel {
    switch (this) {
      case irrigation:
        return 'ري';
      case fertilization:
        return 'تسميد';
      case spraying:
        return 'رش';
      case scouting:
        return 'تفقد';
      case harvesting:
        return 'حصاد';
      case maintenance:
        return 'صيانة';
      case other:
        return 'أخرى';
    }
  }
}

/// أولويات المهام
enum TaskPriority {
  urgent,
  high,
  medium,
  low;

  String get arabicLabel {
    switch (this) {
      case urgent:
        return 'عاجل';
      case high:
        return 'مهم';
      case medium:
        return 'متوسط';
      case low:
        return 'منخفض';
    }
  }
}
