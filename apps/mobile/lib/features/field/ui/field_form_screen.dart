import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة إضافة/تعديل الحقل - Smart Form
/// نموذج بسيط وسهل الاستخدام لإدخال بيانات الحقل
class FieldFormScreen extends StatefulWidget {
  final String? fieldId; // null = إضافة جديد

  const FieldFormScreen({super.key, this.fieldId});

  @override
  State<FieldFormScreen> createState() => _FieldFormScreenState();
}

class _FieldFormScreenState extends State<FieldFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _areaController = TextEditingController();
  
  String? _selectedCrop;
  String? _selectedIrrigation;
  DateTime? _plantingDate;
  bool _hasBoundary = false;

  bool get isEditing => widget.fieldId != null;

  @override
  void dispose() {
    _nameController.dispose();
    _areaController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: Text(isEditing ? "تعديل الحقل" : "إضافة حقل جديد"),
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
              // القسم 1: البيانات الأساسية
              _buildSectionHeader("بيانات الحقل الأساسية", Icons.info_outline),
              const SizedBox(height: 16),

              // اسم الحقل
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: "اسم الحقل",
                  hintText: "مثال: المزرعة الشمالية",
                  prefixIcon: Icon(Icons.label_outline),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'الرجاء إدخال اسم الحقل';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // نوع المحصول
              DropdownButtonFormField<String>(
                value: _selectedCrop,
                decoration: const InputDecoration(
                  labelText: "نوع المحصول",
                  prefixIcon: Icon(Icons.grass),
                ),
                items: const [
                  DropdownMenuItem(value: "wheat", child: Text("قمح")),
                  DropdownMenuItem(value: "corn", child: Text("ذرة")),
                  DropdownMenuItem(value: "tomato", child: Text("طماطم")),
                  DropdownMenuItem(value: "potato", child: Text("بطاطس")),
                  DropdownMenuItem(value: "onion", child: Text("بصل")),
                  DropdownMenuItem(value: "alfalfa", child: Text("برسيم")),
                  DropdownMenuItem(value: "other", child: Text("أخرى")),
                ],
                onChanged: (v) => setState(() => _selectedCrop = v),
                validator: (value) {
                  if (value == null) {
                    return 'الرجاء اختيار نوع المحصول';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // المساحة
              TextFormField(
                controller: _areaController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "المساحة (هكتار)",
                  hintText: "مثال: 2.5",
                  prefixIcon: Icon(Icons.aspect_ratio),
                  suffixText: "هكتار",
                ),
              ),
              const SizedBox(height: 16),

              // نظام الري
              DropdownButtonFormField<String>(
                value: _selectedIrrigation,
                decoration: const InputDecoration(
                  labelText: "نظام الري",
                  prefixIcon: Icon(Icons.water_drop),
                ),
                items: const [
                  DropdownMenuItem(value: "drip", child: Text("تنقيط")),
                  DropdownMenuItem(value: "sprinkler", child: Text("رشاشات")),
                  DropdownMenuItem(value: "flood", child: Text("غمر")),
                  DropdownMenuItem(value: "pivot", child: Text("محوري")),
                  DropdownMenuItem(value: "none", child: Text("بدون ري (مطري)")),
                ],
                onChanged: (v) => setState(() => _selectedIrrigation = v),
              ),
              const SizedBox(height: 16),

              // تاريخ الزراعة
              InkWell(
                onTap: _selectPlantingDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: "تاريخ الزراعة",
                    prefixIcon: Icon(Icons.calendar_today),
                    suffixIcon: Icon(Icons.arrow_drop_down),
                  ),
                  child: Text(
                    _plantingDate != null
                        ? "${_plantingDate!.year}-${_plantingDate!.month.toString().padLeft(2, '0')}-${_plantingDate!.day.toString().padLeft(2, '0')}"
                        : "اختر التاريخ",
                    style: TextStyle(
                      color: _plantingDate != null ? Colors.black : Colors.grey,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // القسم 2: الموقع الجغرافي
              _buildSectionHeader("الموقع الجغرافي", Icons.map_outlined),
              const SizedBox(height: 16),

              // بطاقة الرسم على الخريطة
              _buildMapCard(),

              const SizedBox(height: 32),

              // القسم 3: معلومات إضافية
              _buildSectionHeader("معلومات إضافية (اختياري)", Icons.more_horiz),
              const SizedBox(height: 16),

              // ملاحظات
              TextFormField(
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: "ملاحظات",
                  hintText: "أي معلومات إضافية عن الحقل...",
                  alignLabelWithHint: true,
                  prefixIcon: Padding(
                    padding: EdgeInsets.only(bottom: 50),
                    child: Icon(Icons.notes),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // زر الحفظ
              ElevatedButton(
                onPressed: _saveField,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  isEditing ? "حفظ التغييرات" : "إضافة الحقل",
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

  Widget _buildMapCard() {
    return OrganicCard(
      color: _hasBoundary ? SahoolColors.sageGreen.withOpacity(0.1) : SahoolColors.paleOlive.withOpacity(0.5),
      child: Column(
        children: [
          Icon(
            _hasBoundary ? Icons.check_circle : Icons.map_outlined,
            size: 48,
            color: _hasBoundary ? SahoolColors.sageGreen : SahoolColors.forestGreen,
          ),
          const SizedBox(height: 12),
          Text(
            _hasBoundary ? "تم تحديد الحدود" : "لم يتم تحديد الحدود",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: _hasBoundary ? SahoolColors.sageGreen : SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(height: 8),
          if (_hasBoundary)
            const Text(
              "المساحة: 2.5 هكتار",
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () async {
              final result = await Navigator.pushNamed(context, '/map', arguments: {'mode': 'draw'});
              if (result == true) {
                setState(() => _hasBoundary = true);
              }
            },
            icon: Icon(_hasBoundary ? Icons.edit : Icons.draw),
            label: Text(_hasBoundary ? "تعديل الحدود" : "رسم الحدود على الخريطة"),
            style: OutlinedButton.styleFrom(
              foregroundColor: SahoolColors.forestGreen,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _selectPlantingDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _plantingDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
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
      setState(() => _plantingDate = date);
    }
  }

  void _saveField() {
    if (_formKey.currentState!.validate()) {
      // حفظ البيانات
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(isEditing ? "تم تحديث الحقل بنجاح" : "تم إضافة الحقل بنجاح"),
          backgroundColor: SahoolColors.forestGreen,
        ),
      );
      Navigator.pop(context, true);
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("حذف الحقل"),
        content: const Text("هل أنت متأكد من حذف هذا الحقل؟ لا يمكن التراجع عن هذا الإجراء."),
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
