/// VRA Create Screen - شاشة إنشاء الوصفة
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/vra_models.dart';
import '../providers/vra_provider.dart';
import '../widgets/zone_map_widget.dart';
import 'vra_detail_screen.dart';

/// شاشة إنشاء الوصفة
class VRACreateScreen extends ConsumerStatefulWidget {
  const VRACreateScreen({super.key});

  @override
  ConsumerState<VRACreateScreen> createState() => _VRACreateScreenState();
}

class _VRACreateScreenState extends ConsumerState<VRACreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _nameArController = TextEditingController();
  final _notesController = TextEditingController();
  final _notesArController = TextEditingController();

  String? _selectedFieldId;
  VRAType _selectedVraType = VRAType.fertilizer;
  ZoningMethod _selectedZoningMethod = ZoningMethod.ndvi;
  int _zonesCount = 3;
  DateTime? _scheduledDate;
  List<ManagementZone>? _previewZones;
  bool _isGeneratingZones = false;

  @override
  void dispose() {
    _nameController.dispose();
    _nameArController.dispose();
    _notesController.dispose();
    _notesArController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    return Scaffold(
      appBar: AppBar(
        title: Text(isRTL ? 'إنشاء وصفة جديدة' : 'Create New Prescription'),
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // معلومات أساسية
              _buildSectionTitle(isRTL ? 'معلومات أساسية' : 'Basic Information', isRTL),
              const SizedBox(height: 16),

              // اسم الوصفة
              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: isRTL ? 'اسم الوصفة (English)' : 'Prescription Name (English)',
                  hintText: isRTL ? 'مثال: Fertilizer Application Q1 2024' : 'Example: Fertilizer Application Q1 2024',
                  border: const OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return isRTL ? 'الرجاء إدخال اسم الوصفة' : 'Please enter prescription name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // اسم الوصفة بالعربية
              TextFormField(
                controller: _nameArController,
                decoration: InputDecoration(
                  labelText: isRTL ? 'اسم الوصفة (العربية)' : 'Prescription Name (Arabic)',
                  hintText: isRTL ? 'مثال: تطبيق الأسمدة - الربع الأول 2024' : 'Example: تطبيق الأسمدة - الربع الأول 2024',
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),

              // اختيار الحقل (مبسط - في التطبيق الفعلي يتم جلبه من API)
              DropdownButtonFormField<String>(
                value: _selectedFieldId,
                decoration: InputDecoration(
                  labelText: isRTL ? 'الحقل' : 'Field',
                  border: const OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'field_1', child: Text('Field 1 - حقل رقم 1')),
                  DropdownMenuItem(value: 'field_2', child: Text('Field 2 - حقل رقم 2')),
                  DropdownMenuItem(value: 'field_3', child: Text('Field 3 - حقل رقم 3')),
                ],
                onChanged: (value) => setState(() => _selectedFieldId = value),
                validator: (value) {
                  if (value == null) {
                    return isRTL ? 'الرجاء اختيار الحقل' : 'Please select a field';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // إعدادات VRA
              _buildSectionTitle(isRTL ? 'إعدادات التطبيق المتغير' : 'VRA Settings', isRTL),
              const SizedBox(height: 16),

              // نوع VRA
              DropdownButtonFormField<VRAType>(
                value: _selectedVraType,
                decoration: InputDecoration(
                  labelText: isRTL ? 'النوع' : 'Type',
                  border: const OutlineInputBorder(),
                ),
                items: VRAType.values.map((type) {
                  return DropdownMenuItem(
                    value: type,
                    child: Text(type.getName(locale)),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) setState(() => _selectedVraType = value);
                },
              ),
              const SizedBox(height: 16),

              // طريقة التقسيم
              DropdownButtonFormField<ZoningMethod>(
                value: _selectedZoningMethod,
                decoration: InputDecoration(
                  labelText: isRTL ? 'طريقة تقسيم المناطق' : 'Zoning Method',
                  border: const OutlineInputBorder(),
                ),
                items: ZoningMethod.values.map((method) {
                  return DropdownMenuItem(
                    value: method,
                    child: Text(method.getName(locale)),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) setState(() => _selectedZoningMethod = value);
                },
              ),
              const SizedBox(height: 16),

              // عدد المناطق
              Row(
                children: [
                  Expanded(
                    child: Text(
                      isRTL ? 'عدد المناطق: $_zonesCount' : 'Number of Zones: $_zonesCount',
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.remove_circle_outline),
                    onPressed: _zonesCount > 2
                        ? () => setState(() => _zonesCount--)
                        : null,
                  ),
                  IconButton(
                    icon: const Icon(Icons.add_circle_outline),
                    onPressed: _zonesCount < 10
                        ? () => setState(() => _zonesCount++)
                        : null,
                  ),
                ],
              ),
              Slider(
                value: _zonesCount.toDouble(),
                min: 2,
                max: 10,
                divisions: 8,
                label: _zonesCount.toString(),
                onChanged: (value) => setState(() => _zonesCount = value.toInt()),
              ),
              const SizedBox(height: 16),

              // معاينة المناطق
              if (_selectedFieldId != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            isRTL ? 'معاينة المناطق' : 'Preview Zones',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        FilledButton.tonalIcon(
                          onPressed: _isGeneratingZones ? null : _generatePreviewZones,
                          icon: _isGeneratingZones
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.refresh),
                          label: Text(isRTL ? 'توليد' : 'Generate'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (_previewZones != null)
                      Container(
                        height: 300,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey[300]!),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: ZoneMapWidget(
                            zones: _previewZones!,
                            rates: const [],
                          ),
                        ),
                      )
                    else
                      Container(
                        height: 200,
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          border: Border.all(color: Colors.grey[300]!),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.map_outlined, size: 64, color: Colors.grey[400]),
                              const SizedBox(height: 8),
                              Text(
                                isRTL
                                    ? 'اضغط على "توليد" لمعاينة المناطق'
                                    : 'Tap "Generate" to preview zones',
                                style: TextStyle(color: Colors.grey[600]),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              const SizedBox(height: 24),

              // معلومات إضافية
              _buildSectionTitle(isRTL ? 'معلومات إضافية' : 'Additional Information', isRTL),
              const SizedBox(height: 16),

              // موعد التطبيق
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(isRTL ? 'موعد التطبيق' : 'Scheduled Date'),
                subtitle: Text(
                  _scheduledDate != null
                      ? _scheduledDate.toString().split(' ')[0]
                      : (isRTL ? 'لم يتم تحديد موعد' : 'No date selected'),
                ),
                trailing: const Icon(Icons.calendar_today),
                onTap: _selectScheduledDate,
              ),
              const Divider(),

              // ملاحظات
              TextFormField(
                controller: _notesController,
                decoration: InputDecoration(
                  labelText: isRTL ? 'ملاحظات (English)' : 'Notes (English)',
                  border: const OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _notesArController,
                decoration: InputDecoration(
                  labelText: isRTL ? 'ملاحظات (العربية)' : 'Notes (Arabic)',
                  border: const OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                  ),
                  child: Text(isRTL ? 'إلغاء' : 'Cancel'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                flex: 2,
                child: FilledButton.icon(
                  onPressed: _createPrescription,
                  icon: const Icon(Icons.check),
                  label: Text(isRTL ? 'إنشاء الوصفة' : 'Create Prescription'),
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title, bool isRTL) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Future<void> _selectScheduledDate() async {
    final locale = Localizations.localeOf(context).languageCode;
    final picked = await showDatePicker(
      context: context,
      initialDate: _scheduledDate ?? DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: Locale(locale),
    );

    if (picked != null) {
      setState(() => _scheduledDate = picked);
    }
  }

  Future<void> _generatePreviewZones() async {
    if (_selectedFieldId == null) return;

    setState(() => _isGeneratingZones = true);

    final zones = await ref.read(vraControllerProvider.notifier).generateZones(
          fieldId: _selectedFieldId!,
          zoningMethod: _selectedZoningMethod,
          zonesCount: _zonesCount,
        );

    setState(() {
      _previewZones = zones;
      _isGeneratingZones = false;
    });
  }

  Future<void> _createPrescription() async {
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    if (!_formKey.currentState!.validate()) return;
    if (_selectedFieldId == null) return;

    // عرض مؤشر التحميل
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: 16),
                Text(isRTL ? 'جارٍ إنشاء الوصفة...' : 'Creating prescription...'),
              ],
            ),
          ),
        ),
      ),
    );

    // إنشاء الوصفة
    final prescription = await ref.read(vraControllerProvider.notifier).generatePrescription(
          fieldId: _selectedFieldId!,
          vraType: _selectedVraType,
          zoningMethod: _selectedZoningMethod,
          zonesCount: _zonesCount,
          name: _nameController.text,
          nameAr: _nameArController.text.isEmpty ? null : _nameArController.text,
          scheduledDate: _scheduledDate,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
          notesAr: _notesArController.text.isEmpty ? null : _notesArController.text,
        );

    if (!mounted) return;

    // إغلاق مؤشر التحميل
    Navigator.pop(context);

    if (prescription != null) {
      // عرض رسالة نجاح
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(isRTL ? 'تم إنشاء الوصفة بنجاح' : 'Prescription created successfully'),
          backgroundColor: Colors.green,
        ),
      );

      // الانتقال إلى شاشة التفاصيل
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => VRADetailScreen(prescriptionId: prescription.prescriptionId),
        ),
      );
    } else {
      // عرض رسالة خطأ
      final error = ref.read(vraControllerProvider).error;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error?.toString() ?? (isRTL ? 'فشل في إنشاء الوصفة' : 'Failed to create prescription')),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
