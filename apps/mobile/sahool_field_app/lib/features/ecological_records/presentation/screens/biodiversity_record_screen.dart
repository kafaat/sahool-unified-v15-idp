import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/ecological_providers.dart';
import '../../domain/entities/ecological_entities.dart';

/// شاشة تسجيل مراقبة التنوع البيولوجي
/// Biodiversity Observation Recording Screen
class BiodiversityRecordScreen extends ConsumerStatefulWidget {
  final String? recordId; // null = سجل جديد

  const BiodiversityRecordScreen({super.key, this.recordId});

  @override
  ConsumerState<BiodiversityRecordScreen> createState() => _BiodiversityRecordScreenState();
}

class _BiodiversityRecordScreenState extends ConsumerState<BiodiversityRecordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _speciesCountController = TextEditingController();
  final _beneficialInsectCountController = TextEditingController();
  final _pollinatorCountController = TextEditingController();
  final _notesController = TextEditingController();

  DateTime? _surveyDate;
  String? _selectedSurveyType;
  final Set<String> _selectedHabitatFeatures = {};

  bool get isEditing => widget.recordId != null;

  @override
  void dispose() {
    _speciesCountController.dispose();
    _beneficialInsectCountController.dispose();
    _pollinatorCountController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: Text(isEditing ? "تعديل سجل التنوع البيولوجي" : "تسجيل مراقبة جديدة"),
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
              // القسم 1: بيانات المسح الأساسية
              _buildSectionHeader("بيانات المسح الأساسية", Icons.assignment_outlined),
              const SizedBox(height: 16),

              // تاريخ المسح
              InkWell(
                onTap: _selectSurveyDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: "تاريخ المسح",
                    hintText: "اختر تاريخ المسح",
                    prefixIcon: Icon(Icons.calendar_today),
                    suffixIcon: Icon(Icons.arrow_drop_down),
                  ),
                  child: Text(
                    _surveyDate != null
                        ? "${_surveyDate!.year}-${_surveyDate!.month.toString().padLeft(2, '0')}-${_surveyDate!.day.toString().padLeft(2, '0')}"
                        : "اختر التاريخ",
                    style: TextStyle(
                      color: _surveyDate != null ? Colors.black : Colors.grey,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // نوع المسح
              DropdownButtonFormField<String>(
                value: _selectedSurveyType,
                decoration: const InputDecoration(
                  labelText: "نوع المسح",
                  hintText: "اختر نوع المسح",
                  prefixIcon: Icon(Icons.category_outlined),
                ),
                items: const [
                  DropdownMenuItem(
                    value: "species_count",
                    child: Text("عدد الأنواع"),
                  ),
                  DropdownMenuItem(
                    value: "habitat_assessment",
                    child: Text("تقييم الموئل"),
                  ),
                  DropdownMenuItem(
                    value: "beneficial_insects",
                    child: Text("الحشرات النافعة"),
                  ),
                  DropdownMenuItem(
                    value: "soil_organisms",
                    child: Text("كائنات التربة"),
                  ),
                  DropdownMenuItem(
                    value: "general",
                    child: Text("عام"),
                  ),
                ],
                onChanged: (v) => setState(() => _selectedSurveyType = v),
                validator: (value) {
                  if (value == null) {
                    return 'الرجاء اختيار نوع المسح';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 32),

              // القسم 2: عدد الكائنات الحية
              _buildSectionHeader("عدد الكائنات الحية", Icons.pets_outlined),
              const SizedBox(height: 16),

              // عدد الأنواع الملاحظة
              TextFormField(
                controller: _speciesCountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "عدد الأنواع الملاحظة",
                  hintText: "مثال: 15",
                  prefixIcon: Icon(Icons.diversity_3_outlined),
                  suffixText: "نوع",
                ),
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    final number = int.tryParse(value);
                    if (number == null || number < 0) {
                      return 'الرجاء إدخال رقم صحيح';
                    }
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // عدد الحشرات النافعة
              TextFormField(
                controller: _beneficialInsectCountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "عدد الحشرات النافعة",
                  hintText: "مثال: 25",
                  prefixIcon: Icon(Icons.bug_report_outlined),
                  suffixText: "حشرة",
                ),
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    final number = int.tryParse(value);
                    if (number == null || number < 0) {
                      return 'الرجاء إدخال رقم صحيح';
                    }
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // عدد الملقحات
              TextFormField(
                controller: _pollinatorCountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "عدد الملقحات",
                  hintText: "مثال: 12",
                  prefixIcon: Icon(Icons.flutter_dash_outlined),
                  suffixText: "ملقح",
                ),
                validator: (value) {
                  if (value != null && value.isNotEmpty) {
                    final number = int.tryParse(value);
                    if (number == null || number < 0) {
                      return 'الرجاء إدخال رقم صحيح';
                    }
                  }
                  return null;
                },
              ),

              const SizedBox(height: 32),

              // القسم 3: خصائص الموئل
              _buildSectionHeader("خصائص الموئل", Icons.landscape_outlined),
              const SizedBox(height: 16),

              // بطاقة اختيار خصائص الموئل
              _buildHabitatFeaturesCard(),

              const SizedBox(height: 32),

              // القسم 4: ملاحظات إضافية
              _buildSectionHeader("ملاحظات إضافية", Icons.note_outlined),
              const SizedBox(height: 16),

              // ملاحظات
              TextFormField(
                controller: _notesController,
                maxLines: 5,
                decoration: const InputDecoration(
                  labelText: "ملاحظات",
                  hintText: "أي معلومات إضافية عن المسح أو الملاحظات...",
                  alignLabelWithHint: true,
                  prefixIcon: Padding(
                    padding: EdgeInsets.only(bottom: 80),
                    child: Icon(Icons.notes),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // زر الحفظ
              ElevatedButton(
                onPressed: _saveRecord,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  isEditing ? "حفظ التغييرات" : "حفظ السجل",
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

  Widget _buildHabitatFeaturesCard() {
    final features = [
      _HabitatFeature(
        id: 'trees',
        label: 'أشجار',
        icon: Icons.park_outlined,
      ),
      _HabitatFeature(
        id: 'shrubs',
        label: 'شجيرات',
        icon: Icons.grass_outlined,
      ),
      _HabitatFeature(
        id: 'wildflowers',
        label: 'أزهار برية',
        icon: Icons.local_florist_outlined,
      ),
      _HabitatFeature(
        id: 'water_sources',
        label: 'مصادر مياه',
        icon: Icons.water_drop_outlined,
      ),
      _HabitatFeature(
        id: 'hedges',
        label: 'أسيجة',
        icon: Icons.fence_outlined,
      ),
    ];

    return OrganicCard(
      color: SahoolColors.paleOlive.withOpacity(0.5),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.check_box_outlined,
                size: 20,
                color: SahoolColors.forestGreen,
              ),
              const SizedBox(width: 8),
              const Text(
                "اختر الخصائص المتوفرة",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                  color: SahoolColors.forestGreen,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: features.map((feature) {
              final isSelected = _selectedHabitatFeatures.contains(feature.id);
              return FilterChip(
                selected: isSelected,
                label: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      feature.icon,
                      size: 16,
                      color: isSelected ? SahoolColors.forestGreen : SahoolColors.textSecondary,
                    ),
                    const SizedBox(width: 4),
                    Text(feature.label),
                  ],
                ),
                onSelected: (selected) {
                  setState(() {
                    if (selected) {
                      _selectedHabitatFeatures.add(feature.id);
                    } else {
                      _selectedHabitatFeatures.remove(feature.id);
                    }
                  });
                },
                selectedColor: SahoolColors.sageGreen.withOpacity(0.3),
                checkmarkColor: SahoolColors.forestGreen,
                backgroundColor: Colors.white,
                side: BorderSide(
                  color: isSelected ? SahoolColors.sageGreen : Colors.grey.shade300,
                  width: isSelected ? 2 : 1,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              );
            }).toList(),
          ),
          if (_selectedHabitatFeatures.isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: SahoolColors.sageGreen.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.check_circle,
                    size: 16,
                    color: SahoolColors.sageGreen,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    "${_selectedHabitatFeatures.length} خاصية محددة",
                    style: TextStyle(
                      fontSize: 12,
                      color: SahoolColors.forestGreen,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _selectSurveyDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _surveyDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
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
      setState(() => _surveyDate = date);
    }
  }

  void _saveRecord() async {
    if (_formKey.currentState!.validate()) {
      // التحقق من أن تاريخ المسح محدد
      if (_surveyDate == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("الرجاء تحديد تاريخ المسح"),
            backgroundColor: SahoolColors.danger,
          ),
        );
        return;
      }

      // التحقق من وجود بيانات على الأقل
      final hasData = _speciesCountController.text.isNotEmpty ||
          _beneficialInsectCountController.text.isNotEmpty ||
          _pollinatorCountController.text.isNotEmpty ||
          _selectedHabitatFeatures.isNotEmpty ||
          _notesController.text.isNotEmpty;

      if (!hasData) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("الرجاء إدخال بيانات للسجل"),
            backgroundColor: SahoolColors.danger,
          ),
        );
        return;
      }

      // حفظ البيانات
      final BiodiversitySurveyType surveyType = _parseSurveyType(_selectedSurveyType);

      final record = BiodiversityRecord(
        id: widget.recordId ?? DateTime.now().millisecondsSinceEpoch.toString(),
        farmId: 'default_farm', // TODO: Get from context or parameter
        surveyDate: _surveyDate!,
        surveyType: surveyType,
        speciesObserved: _speciesCountController.text.isNotEmpty
            ? int.parse(_speciesCountController.text)
            : 0,
        beneficialInsectsCount: _beneficialInsectCountController.text.isNotEmpty
            ? int.parse(_beneficialInsectCountController.text)
            : null,
        pollinatorsCount: _pollinatorCountController.text.isNotEmpty
            ? int.parse(_pollinatorCountController.text)
            : null,
        habitatFeatures: _selectedHabitatFeatures.toList(),
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );

      // حفظ السجل باستخدام المزود
      await ref.read(biodiversityProvider.notifier).addRecord(record);

      // عرض رسالة نجاح
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم حفظ السجل بنجاح'),
            backgroundColor: SahoolColors.forestGreen,
          ),
        );

        // العودة للشاشة السابقة
        Navigator.pop(context);
      }
    }
  }

  BiodiversitySurveyType _parseSurveyType(String? type) {
    switch (type) {
      case 'species_count':
        return BiodiversitySurveyType.speciesCount;
      case 'habitat_assessment':
        return BiodiversitySurveyType.habitatAssessment;
      case 'beneficial_insects':
        return BiodiversitySurveyType.beneficialInsects;
      case 'soil_organisms':
        return BiodiversitySurveyType.soilOrganisms;
      default:
        return BiodiversitySurveyType.general;
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("حذف السجل"),
        content: const Text("هل أنت متأكد من حذف هذا السجل؟ لا يمكن التراجع عن هذا الإجراء."),
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

/// نموذج بيانات خصائص الموئل
class _HabitatFeature {
  final String id;
  final String label;
  final IconData icon;

  _HabitatFeature({
    required this.id,
    required this.label,
    required this.icon,
  });
}
