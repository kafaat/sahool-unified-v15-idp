import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';

/// شاشة تسجيل تطبيق الممارسات البيئية
/// Ecological Practice Implementation Record Screen
class PracticeRecordScreen extends StatefulWidget {
  final String? recordId; // null = إضافة جديد

  const PracticeRecordScreen({super.key, this.recordId});

  @override
  State<PracticeRecordScreen> createState() => _PracticeRecordScreenState();
}

class _PracticeRecordScreenState extends State<PracticeRecordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _laborHoursController = TextEditingController();
  final _costEstimateController = TextEditingController();
  final _notesController = TextEditingController();

  String? _selectedPractice;
  String? _selectedStatus;
  DateTime? _startDate;
  DateTime? _implementationDate;
  List<String> _materialsUsed = [];
  int _effectivenessRating = 0;
  List<String> _observedBenefits = [];
  List<String> _challenges = [];

  // Controllers for chips input
  final _materialInputController = TextEditingController();
  final _benefitInputController = TextEditingController();
  final _challengeInputController = TextEditingController();

  bool get isEditing => widget.recordId != null;

  // Practice options with Arabic translations
  final Map<String, String> _practiceOptions = {
    'composting': 'التسميد العضوي',
    'no_till': 'الزراعة بدون حراثة',
    'companion_planting': 'الزراعة التصاحبية',
    'biological_control': 'المكافحة البيولوجية',
    'agroforestry': 'الزراعة الحراجية',
    'drip_irrigation': 'الري بالتنقيط',
    'cover_crops': 'محاصيل التغطية',
    'mulching': 'التغطية العضوية',
  };

  // Status options with Arabic translations
  final Map<String, String> _statusOptions = {
    'planned': 'مخطط لها',
    'in_progress': 'جاري التنفيذ',
    'completed': 'تم التنفيذ',
    'paused': 'متوقف',
  };

  // Calculate progress based on status
  double get _progressValue {
    switch (_selectedStatus) {
      case 'planned':
        return 0.25;
      case 'in_progress':
        return 0.5;
      case 'completed':
        return 1.0;
      case 'paused':
        return 0.75;
      default:
        return 0.0;
    }
  }

  Color get _progressColor {
    switch (_selectedStatus) {
      case 'planned':
        return SahoolColors.info;
      case 'in_progress':
        return SahoolColors.warning;
      case 'completed':
        return SahoolColors.success;
      case 'paused':
        return SahoolColors.danger;
      default:
        return Colors.grey;
    }
  }

  @override
  void dispose() {
    _laborHoursController.dispose();
    _costEstimateController.dispose();
    _notesController.dispose();
    _materialInputController.dispose();
    _benefitInputController.dispose();
    _challengeInputController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: Text(isEditing ? "تعديل تسجيل الممارسة" : "تسجيل ممارسة جديدة"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          if (isEditing)
            IconButton(
              icon: const Icon(Icons.delete_outline, color: SahoolColors.danger),
              onPressed: _showDeleteConfirmation,
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Progress Indicator
              if (_selectedStatus != null) _buildProgressIndicator(),
              if (_selectedStatus != null) const SizedBox(height: 24),

              // القسم 1: تفاصيل الممارسة
              _buildSectionHeader("تفاصيل الممارسة", Icons.eco_outlined),
              const SizedBox(height: 16),

              // نوع الممارسة
              DropdownButtonFormField<String>(
                value: _selectedPractice,
                decoration: const InputDecoration(
                  labelText: "الممارسة",
                  hintText: "اختر نوع الممارسة البيئية",
                  prefixIcon: Icon(Icons.nature_people),
                ),
                items: _practiceOptions.entries.map((entry) {
                  return DropdownMenuItem(
                    value: entry.key,
                    child: Text(entry.value),
                  );
                }).toList(),
                onChanged: (v) => setState(() => _selectedPractice = v),
                validator: (value) {
                  if (value == null) {
                    return 'الرجاء اختيار نوع الممارسة';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 32),

              // القسم 2: حالة التنفيذ
              _buildSectionHeader("حالة التنفيذ", Icons.track_changes_outlined),
              const SizedBox(height: 16),

              // الحالة
              DropdownButtonFormField<String>(
                value: _selectedStatus,
                decoration: const InputDecoration(
                  labelText: "الحالة",
                  prefixIcon: Icon(Icons.flag_outlined),
                ),
                items: _statusOptions.entries.map((entry) {
                  return DropdownMenuItem(
                    value: entry.key,
                    child: Text(entry.value),
                  );
                }).toList(),
                onChanged: (v) => setState(() => _selectedStatus = v),
                validator: (value) {
                  if (value == null) {
                    return 'الرجاء اختيار الحالة';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // تاريخ البدء
              InkWell(
                onTap: () => _selectDate(context, true),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: "تاريخ البدء",
                    prefixIcon: Icon(Icons.calendar_today),
                    suffixIcon: Icon(Icons.arrow_drop_down),
                  ),
                  child: Text(
                    _startDate != null
                        ? _formatDate(_startDate!)
                        : "اختر تاريخ البدء",
                    style: TextStyle(
                      color: _startDate != null ? Colors.black : Colors.grey,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // تاريخ الاكتمال
              InkWell(
                onTap: () => _selectDate(context, false),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: "تاريخ الاكتمال",
                    prefixIcon: Icon(Icons.event_available),
                    suffixIcon: Icon(Icons.arrow_drop_down),
                  ),
                  child: Text(
                    _implementationDate != null
                        ? _formatDate(_implementationDate!)
                        : "اختر تاريخ الاكتمال (اختياري)",
                    style: TextStyle(
                      color: _implementationDate != null ? Colors.black : Colors.grey,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // القسم 3: الموارد المستخدمة
              _buildSectionHeader("الموارد المستخدمة", Icons.inventory_2_outlined),
              const SizedBox(height: 16),

              // المواد المستخدمة
              _buildChipsInput(
                label: "المواد المستخدمة",
                hint: "أضف المواد المستخدمة",
                controller: _materialInputController,
                chips: _materialsUsed,
                icon: Icons.shopping_basket_outlined,
                onAdd: (value) {
                  if (value.isNotEmpty) {
                    setState(() {
                      _materialsUsed.add(value);
                      _materialInputController.clear();
                    });
                  }
                },
                onDelete: (index) {
                  setState(() => _materialsUsed.removeAt(index));
                },
              ),
              const SizedBox(height: 16),

              // ساعات العمل
              TextFormField(
                controller: _laborHoursController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "ساعات العمل",
                  hintText: "مثال: 40",
                  prefixIcon: Icon(Icons.access_time),
                  suffixText: "ساعة",
                ),
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    final hours = double.tryParse(value);
                    if (hours == null || hours < 0) {
                      return 'الرجاء إدخال قيمة صحيحة';
                    }
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // التكلفة التقديرية
              TextFormField(
                controller: _costEstimateController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "التكلفة التقديرية",
                  hintText: "مثال: 5000",
                  prefixIcon: Icon(Icons.attach_money),
                  suffixText: "ريال",
                ),
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    final cost = double.tryParse(value);
                    if (cost == null || cost < 0) {
                      return 'الرجاء إدخال قيمة صحيحة';
                    }
                  }
                  return null;
                },
              ),
              const SizedBox(height: 32),

              // القسم 4: النتائج والتقييم
              _buildSectionHeader("النتائج والتقييم", Icons.assessment_outlined),
              const SizedBox(height: 16),

              // تقييم الفعالية
              _buildEffectivenessRating(),
              const SizedBox(height: 16),

              // الفوائد الملاحظة
              _buildChipsInput(
                label: "الفوائد الملاحظة",
                hint: "أضف الفوائد الملاحظة",
                controller: _benefitInputController,
                chips: _observedBenefits,
                icon: Icons.thumb_up_outlined,
                onAdd: (value) {
                  if (value.isNotEmpty) {
                    setState(() {
                      _observedBenefits.add(value);
                      _benefitInputController.clear();
                    });
                  }
                },
                onDelete: (index) {
                  setState(() => _observedBenefits.removeAt(index));
                },
              ),
              const SizedBox(height: 16),

              // التحديات
              _buildChipsInput(
                label: "التحديات",
                hint: "أضف التحديات التي واجهتك",
                controller: _challengeInputController,
                chips: _challenges,
                icon: Icons.warning_amber_outlined,
                onAdd: (value) {
                  if (value.isNotEmpty) {
                    setState(() {
                      _challenges.add(value);
                      _challengeInputController.clear();
                    });
                  }
                },
                onDelete: (index) {
                  setState(() => _challenges.removeAt(index));
                },
              ),
              const SizedBox(height: 16),

              // ملاحظات التنفيذ
              TextFormField(
                controller: _notesController,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: "ملاحظات التنفيذ",
                  hintText: "أي معلومات إضافية عن تطبيق الممارسة...",
                  alignLabelWithHint: true,
                  prefixIcon: Padding(
                    padding: EdgeInsets.only(bottom: 70),
                    child: Icon(Icons.notes),
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // زر الحفظ
              ElevatedButton(
                onPressed: _savePracticeRecord,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  isEditing ? "حفظ التغييرات" : "حفظ التسجيل",
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // زر إلغاء
              OutlinedButton(
                onPressed: () => Navigator.pop(context),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text("إلغاء"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: SahoolColors.forestGreen),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: SahoolColors.forestGreen,
          ),
        ),
      ],
    );
  }

  Widget _buildProgressIndicator() {
    return OrganicCard(
      color: _progressColor.withOpacity(0.1),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "حالة التنفيذ",
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: _progressColor,
                ),
              ),
              Text(
                _statusOptions[_selectedStatus] ?? '',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: _progressColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: _progressValue,
              backgroundColor: Colors.grey.withOpacity(0.2),
              valueColor: AlwaysStoppedAnimation<Color>(_progressColor),
              minHeight: 12,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "${(_progressValue * 100).toInt()}% مكتمل",
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEffectivenessRating() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "تقييم الفعالية",
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: SahoolColors.textSecondary,
          ),
        ),
        const SizedBox(height: 12),
        OrganicCard(
          color: Colors.white,
          padding: const EdgeInsets.all(16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(5, (index) {
              final starIndex = index + 1;
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _effectivenessRating = starIndex;
                  });
                },
                child: Icon(
                  starIndex <= _effectivenessRating
                      ? Icons.star
                      : Icons.star_border,
                  size: 40,
                  color: starIndex <= _effectivenessRating
                      ? SahoolColors.harvestGold
                      : Colors.grey[400],
                ),
              );
            }),
          ),
        ),
        if (_effectivenessRating > 0)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              _getRatingDescription(_effectivenessRating),
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
      ],
    );
  }

  String _getRatingDescription(int rating) {
    switch (rating) {
      case 1:
        return "غير فعالة";
      case 2:
        return "فعالية ضعيفة";
      case 3:
        return "فعالية متوسطة";
      case 4:
        return "فعالية جيدة";
      case 5:
        return "فعالية ممتازة";
      default:
        return "";
    }
  }

  Widget _buildChipsInput({
    required String label,
    required String hint,
    required TextEditingController controller,
    required List<String> chips,
    required IconData icon,
    required Function(String) onAdd,
    required Function(int) onDelete,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextFormField(
          controller: controller,
          decoration: InputDecoration(
            labelText: label,
            hintText: hint,
            prefixIcon: Icon(icon),
            suffixIcon: IconButton(
              icon: const Icon(Icons.add_circle, color: SahoolColors.forestGreen),
              onPressed: () => onAdd(controller.text.trim()),
            ),
          ),
          onFieldSubmitted: (value) => onAdd(value.trim()),
        ),
        if (chips.isNotEmpty) ...[
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: chips.asMap().entries.map((entry) {
              return Chip(
                label: Text(entry.value),
                backgroundColor: SahoolColors.paleOlive,
                deleteIcon: const Icon(Icons.close, size: 18),
                onDeleted: () => onDelete(entry.key),
                labelStyle: const TextStyle(
                  color: SahoolColors.forestGreen,
                  fontSize: 13,
                ),
              );
            }).toList(),
          ),
        ],
      ],
    );
  }

  Future<void> _selectDate(BuildContext context, bool isStartDate) async {
    final date = await showDatePicker(
      context: context,
      initialDate: isStartDate
          ? (_startDate ?? DateTime.now())
          : (_implementationDate ?? DateTime.now()),
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: SahoolColors.forestGreen,
            ),
          ),
          child: child!,
        );
      },
    );

    if (date != null) {
      setState(() {
        if (isStartDate) {
          _startDate = date;
        } else {
          _implementationDate = date;
        }
      });
    }
  }

  String _formatDate(DateTime date) {
    return "${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}";
  }

  void _savePracticeRecord() {
    if (_formKey.currentState!.validate()) {
      // Validate at least one material is added if labor hours or cost is provided
      if ((_laborHoursController.text.isNotEmpty ||
           _costEstimateController.text.isNotEmpty) &&
          _materialsUsed.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("الرجاء إضافة المواد المستخدمة"),
            backgroundColor: SahoolColors.warning,
          ),
        );
        return;
      }

      // Validate start date is before implementation date
      if (_startDate != null && _implementationDate != null) {
        if (_implementationDate!.isBefore(_startDate!)) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text("تاريخ الاكتمال يجب أن يكون بعد تاريخ البدء"),
              backgroundColor: SahoolColors.danger,
            ),
          );
          return;
        }
      }

      // Build the data object
      final practiceData = {
        'practiceId': _selectedPractice,
        'status': _selectedStatus,
        'startDate': _startDate?.toIso8601String(),
        'implementationDate': _implementationDate?.toIso8601String(),
        'materialsUsed': _materialsUsed,
        'laborHours': _laborHoursController.text.isNotEmpty
            ? double.parse(_laborHoursController.text)
            : null,
        'costEstimate': _costEstimateController.text.isNotEmpty
            ? double.parse(_costEstimateController.text)
            : null,
        'effectivenessRating': _effectivenessRating > 0 ? _effectivenessRating : null,
        'observedBenefits': _observedBenefits,
        'challenges': _challenges,
        'notes': _notesController.text.trim(),
      };

      // TODO: Save to database/repository
      print('Practice Record Data: $practiceData');

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isEditing ? "تم تحديث التسجيل بنجاح" : "تم حفظ التسجيل بنجاح",
          ),
          backgroundColor: SahoolColors.success,
        ),
      );
      Navigator.pop(context, true);
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("حذف التسجيل"),
        content: const Text(
          "هل أنت متأكد من حذف هذا التسجيل؟ لا يمكن التراجع عن هذا الإجراء.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("إلغاء"),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context, 'deleted'); // Return to previous screen
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.danger,
            ),
            child: const Text("حذف", style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}
