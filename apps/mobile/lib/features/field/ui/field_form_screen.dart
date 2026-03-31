import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../../../core/accessibility/semantics_helper.dart';
import '../../../core/http/api_client.dart';
import '../../../core/di/providers.dart';
import '../../../core/iam/iam_providers.dart';
import '../../crops/data/models/crop_model.dart';
import '../../crops/data/remote/crops_api.dart';
import '../../crops/data/repositories/crops_repository.dart';

/// شاشة إضافة/تعديل الحقل - Smart Form
/// نموذج بسيط وسهل الاستخدام لإدخال بيانات الحقل
///
/// Accessibility Features:
/// - Semantic labels for all form fields
/// - Error announcements for screen readers
/// - Focus management
/// - Minimum touch targets
class FieldFormScreen extends ConsumerStatefulWidget {
  final String? fieldId; // null = إضافة جديد

  const FieldFormScreen({super.key, this.fieldId});

  @override
  ConsumerState<FieldFormScreen> createState() => _FieldFormScreenState();
}

class _FieldFormScreenState extends ConsumerState<FieldFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _areaController = TextEditingController();

  String? _selectedCrop;
  String? _selectedIrrigation;
  DateTime? _plantingDate;
  bool _hasBoundary = false;

  bool _isSaving = false;

  // Crops data
  List<Crop> _crops = [];
  bool _isLoadingCrops = true;
  String? _cropsError;
  late CropsRepository _cropsRepository;

  bool get isEditing => widget.fieldId != null;

  @override
  void initState() {
    super.initState();
    _initializeCropsRepository();
  }

  Future<void> _initializeCropsRepository() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final apiClient = ApiClient();
      final cropsApi = CropsApi(apiClient);
      _cropsRepository = CropsRepository(api: cropsApi, prefs: prefs);

      await _loadCrops();
    } catch (e) {
      setState(() {
        _cropsError = 'فشل تحميل قائمة المحاصيل';
        _isLoadingCrops = false;
      });
    }
  }

  Future<void> _loadCrops() async {
    setState(() {
      _isLoadingCrops = true;
      _cropsError = null;
    });

    try {
      final crops = await _cropsRepository.getAllCrops();
      setState(() {
        _crops = crops;
        _isLoadingCrops = false;
      });
    } catch (e) {
      setState(() {
        _cropsError = 'فشل تحميل قائمة المحاصيل';
        _isLoadingCrops = false;
      });
    }
  }

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
        title: Semantics(
          header: true,
          child: Text(isEditing ? 'تعديل الحقل' : 'إضافة حقل جديد'),
        ),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          if (isEditing)
            Semantics(
              label: SahoolSemantics.deleteButton,
              button: true,
              child: IconButton(
                icon: const Icon(Icons.delete_outline, color: SahoolColors.danger),
                onPressed: _showDeleteConfirmation,
                tooltip: 'حذف الحقل',
              ),
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
              // القسم 1: البيانات الأساسية - Section 1: Basic data
              _buildSectionHeader('بيانات الحقل الأساسية', Icons.info_outline),
              const SizedBox(height: 16),

              // اسم الحقل - Field name
              Semantics(
                label: SahoolSemantics.fieldNameInput,
                textField: true,
                child: TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'اسم الحقل',
                    hintText: 'مثال: المزرعة الشمالية',
                    prefixIcon: ExcludeSemantics(child: Icon(Icons.label_outline)),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'الرجاء إدخال اسم الحقل';
                    }
                    return null;
                  },
                  textInputAction: TextInputAction.next,
                ),
              ),
              const SizedBox(height: 16),

              // نوع المحصول - Crop type
              _buildCropDropdown(),
              const SizedBox(height: 16),

              // المساحة - Area
              Semantics(
                label: SahoolSemantics.areaInput,
                textField: true,
                child: TextFormField(
                  controller: _areaController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'المساحة (هكتار)',
                    hintText: 'مثال: 2.5',
                    prefixIcon: ExcludeSemantics(child: Icon(Icons.aspect_ratio)),
                    suffixText: 'هكتار',
                  ),
                  textInputAction: TextInputAction.next,
                ),
              ),
              const SizedBox(height: 16),

              // نظام الري - Irrigation system
              Semantics(
                label: SahoolSemantics.irrigationDropdown,
                child: DropdownButtonFormField<String>(
                  value: _selectedIrrigation,
                  decoration: const InputDecoration(
                    labelText: 'نظام الري',
                    prefixIcon: ExcludeSemantics(child: Icon(Icons.water_drop)),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'drip', child: Text('تنقيط')),
                    DropdownMenuItem(value: 'sprinkler', child: Text('رشاشات')),
                    DropdownMenuItem(value: 'flood', child: Text('غمر')),
                    DropdownMenuItem(value: 'pivot', child: Text('محوري')),
                    DropdownMenuItem(value: 'none', child: Text('بدون ري (مطري)')),
                  ],
                  onChanged: (v) => setState(() => _selectedIrrigation = v),
                ),
              ),
              const SizedBox(height: 16),

              // تاريخ الزراعة - Planting date
              Semantics(
                label: SahoolSemantics.datePickerButton,
                hint: _plantingDate != null
                    ? 'التاريخ المحدد: ${_plantingDate!.year}-${_plantingDate!.month}-${_plantingDate!.day}'
                    : 'لم يتم تحديد تاريخ',
                button: true,
                child: InkWell(
                  onTap: _selectPlantingDate,
                  child: InputDecorator(
                    decoration: const InputDecoration(
                      labelText: 'تاريخ الزراعة',
                      prefixIcon: ExcludeSemantics(child: Icon(Icons.calendar_today)),
                      suffixIcon: ExcludeSemantics(child: Icon(Icons.arrow_drop_down)),
                    ),
                    child: Text(
                      _plantingDate != null
                          ? "${_plantingDate!.year}-${_plantingDate!.month.toString().padLeft(2, '0')}-${_plantingDate!.day.toString().padLeft(2, '0')}"
                          : 'اختر التاريخ',
                      style: TextStyle(
                        color: _plantingDate != null ? Colors.black : Colors.grey,
                      ),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // القسم 2: الموقع الجغرافي - Section 2: Geographic location
              _buildSectionHeader('الموقع الجغرافي', Icons.map_outlined),
              const SizedBox(height: 16),

              // بطاقة الرسم على الخريطة - Map drawing card
              _buildMapCard(),

              const SizedBox(height: 32),

              // القسم 3: معلومات إضافية - Section 3: Additional info
              _buildSectionHeader('معلومات إضافية (اختياري)', Icons.more_horiz),
              const SizedBox(height: 16),

              // ملاحظات - Notes
              Semantics(
                label: 'حقل الملاحظات، اختياري',
                textField: true,
                child: TextFormField(
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'ملاحظات',
                    hintText: 'أي معلومات إضافية عن الحقل...',
                    alignLabelWithHint: true,
                    prefixIcon: ExcludeSemantics(
                      child: Padding(
                        padding: EdgeInsets.only(bottom: 50),
                        child: Icon(Icons.notes),
                      ),
                    ),
                  ),
                  textInputAction: TextInputAction.done,
                ),
              ),

              const SizedBox(height: 32),

              // زر الحفظ - Save button
              Semantics(
                label: SahoolSemantics.saveButton,
                hint: isEditing ? 'حفظ التغييرات على الحقل' : 'إضافة الحقل الجديد',
                button: true,
                child: SizedBox(
                  height: kMinTouchTargetSize,
                  child: ElevatedButton(
                    onPressed: _isSaving ? null : _saveField,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: SahoolColors.forestGreen,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isSaving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : Text(
                            isEditing ? 'حفظ التغييرات' : 'إضافة الحقل',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // زر إلغاء - Cancel button
              Semantics(
                label: SahoolSemantics.cancelButton,
                button: true,
                child: SizedBox(
                  height: kMinTouchTargetSize,
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text('إلغاء'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Semantics(
      header: true,
      child: Row(
        children: [
          ExcludeSemantics(
            child: Icon(icon, size: 20, color: SahoolColors.forestGreen),
          ),
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
      ),
    );
  }

  Widget _buildCropDropdown() {
    if (_isLoadingCrops) {
      return Semantics(
        label: 'جاري تحميل قائمة المحاصيل',
        child: const InputDecorator(
          decoration: InputDecoration(
            labelText: 'نوع المحصول',
            prefixIcon: ExcludeSemantics(child: Icon(Icons.grass)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              SizedBox(width: 8),
              Text('جاري التحميل...', style: TextStyle(fontSize: 12)),
            ],
          ),
        ),
      );
    }

    if (_cropsError != null) {
      return Semantics(
        label: 'خطأ في تحميل المحاصيل',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            InputDecorator(
              decoration: const InputDecoration(
                labelText: 'نوع المحصول',
                prefixIcon: ExcludeSemantics(child: Icon(Icons.grass)),
              ),
              child: Text(
                _cropsError!,
                style: const TextStyle(color: Colors.red, fontSize: 12),
              ),
            ),
            const SizedBox(height: 8),
            Semantics(
              label: 'إعادة تحميل قائمة المحاصيل',
              button: true,
              child: TextButton.icon(
                onPressed: _loadCrops,
                icon: const Icon(Icons.refresh),
                label: const Text('إعادة المحاولة'),
              ),
            ),
          ],
        ),
      );
    }

    if (_crops.isEmpty) {
      return Semantics(
        label: 'لا توجد محاصيل متاحة',
        child: const InputDecorator(
          decoration: InputDecoration(
            labelText: 'نوع المحصول',
            prefixIcon: ExcludeSemantics(child: Icon(Icons.grass)),
          ),
          child: Text(
            'لا توجد محاصيل متاحة',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ),
      );
    }

    return Semantics(
      label: SahoolSemantics.cropTypeDropdown,
      child: DropdownButtonFormField<String>(
        value: _selectedCrop,
        decoration: InputDecoration(
          labelText: 'نوع المحصول',
          prefixIcon: const ExcludeSemantics(child: Icon(Icons.grass)),
          suffixIcon: _crops.length > 10
              ? Semantics(
                  label: 'البحث عن محصول',
                  button: true,
                  child: IconButton(
                    icon: const Icon(Icons.search, size: 20),
                    onPressed: _showCropSearchDialog,
                    tooltip: 'البحث عن محصول',
                  ),
                )
              : null,
        ),
        items: _crops.map((crop) {
          return DropdownMenuItem<String>(
            value: crop.code,
            child: Semantics(
              label: '${crop.nameAr}، ${crop.nameEn}',
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      crop.nameAr,
                      style: const TextStyle(fontWeight: FontWeight.w500),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    crop.nameEn,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
        onChanged: (v) => setState(() => _selectedCrop = v),
        validator: (value) {
          if (value == null) {
            return 'الرجاء اختيار نوع المحصول';
          }
          return null;
        },
        isExpanded: true,
        menuMaxHeight: 400,
      ),
    );
  }

  Future<void> _showCropSearchDialog() async {
    String searchQuery = '';
    final selectedCrop = await showDialog<Crop>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) {
          final filteredCrops = searchQuery.isEmpty
              ? _crops
              : _crops.where((crop) {
                  final query = searchQuery.toLowerCase();
                  return crop.nameAr.contains(searchQuery) ||
                      crop.nameEn.toLowerCase().contains(query);
                }).toList();

          return AlertDialog(
            title: const Text('اختر المحصول'),
            content: SizedBox(
              width: double.maxFinite,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'البحث',
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(),
                    ),
                    onChanged: (value) {
                      setDialogState(() {
                        searchQuery = value;
                      });
                    },
                    autofocus: true,
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: ListView.builder(
                      shrinkWrap: true,
                      itemCount: filteredCrops.length,
                      itemBuilder: (context, index) {
                        final crop = filteredCrops[index];
                        return ListTile(
                          title: Text(crop.nameAr),
                          subtitle: Text(
                            '${crop.nameEn} • ${crop.category.nameAr}',
                            style: const TextStyle(fontSize: 12),
                          ),
                          onTap: () => Navigator.pop(context, crop),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('إلغاء'),
              ),
            ],
          );
        },
      ),
    );

    if (selectedCrop != null) {
      setState(() {
        _selectedCrop = selectedCrop.code;
      });
    }
  }

  Widget _buildMapCard() {
    return Semantics(
      label: _hasBoundary
          ? 'تم تحديد حدود الحقل، المساحة 2.5 هكتار'
          : 'لم يتم تحديد حدود الحقل',
      child: OrganicCard(
        color: _hasBoundary ? SahoolColors.sageGreen.withValues(alpha: 0.1) : SahoolColors.paleOlive.withValues(alpha: 0.5),
        child: Column(
          children: [
            ExcludeSemantics(
              child: Icon(
                _hasBoundary ? Icons.check_circle : Icons.map_outlined,
                size: 48,
                color: _hasBoundary ? SahoolColors.sageGreen : SahoolColors.forestGreen,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _hasBoundary ? 'تم تحديد الحدود' : 'لم يتم تحديد الحدود',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: _hasBoundary ? SahoolColors.sageGreen : SahoolColors.forestGreen,
              ),
            ),
            const SizedBox(height: 8),
            if (_hasBoundary)
              const Text(
                'المساحة: 2.5 هكتار',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
            const SizedBox(height: 12),
            Semantics(
              label: _hasBoundary ? 'تعديل حدود الحقل' : 'رسم حدود الحقل على الخريطة',
              hint: 'سيتم فتح الخريطة لرسم الحدود',
              button: true,
              child: SizedBox(
                height: kMinTouchTargetSize,
                child: OutlinedButton.icon(
                  onPressed: () async {
                    final result = await Navigator.pushNamed(context, '/map', arguments: {'mode': 'draw'});
                    if (result == true) {
                      setState(() => _hasBoundary = true);
                      if (mounted) AnnouncementHelper.announceComplete(context, 'تحديد الحدود');
                    }
                  },
                  icon: Icon(_hasBoundary ? Icons.edit : Icons.draw),
                  label: Text(_hasBoundary ? 'تعديل الحدود' : 'رسم الحدود على الخريطة'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: SahoolColors.forestGreen,
                  ),
                ),
              ),
            ),
          ],
        ),
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

  Future<void> _saveField() async {
    if (!_formKey.currentState!.validate()) {
      // Announce validation errors
      AnnouncementHelper.announceError(context, 'يرجى تصحيح الأخطاء في النموذج');
      return;
    }

    if (_isSaving) return;
    setState(() => _isSaving = true);

    try {
      final repo = ref.read(fieldsRepoProvider);
      final tenant = ref.read(currentTenantProvider);
      final tenantId = tenant?.id ?? 'default';

      if (isEditing) {
        // تحديث الحقل - Update existing field
        await repo.updateFieldProperties(
          fieldId: widget.fieldId!,
          name: _nameController.text.trim(),
          cropType: _selectedCrop,
        );
      } else {
        // إنشاء حقل جديد - Create new field
        // الحدود ستُضاف من الخريطة لاحقاً - Boundary added via map later
        await repo.createField(
          tenantId: tenantId,
          name: _nameController.text.trim(),
          boundary: const [], // valid: empty boundary, user draws later
          cropType: _selectedCrop,
        );
      }

      if (!mounted) return;

      final message = isEditing ? 'تم تحديث الحقل بنجاح' : 'تم إضافة الحقل بنجاح';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: SahoolColors.forestGreen,
        ),
      );
      // Announce success to screen readers
      AnnouncementHelper.announceComplete(context, isEditing ? 'تحديث الحقل' : 'إضافة الحقل');
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('فشل حفظ الحقل: $e'),
          backgroundColor: SahoolColors.danger,
        ),
      );
      AnnouncementHelper.announceError(context, 'فشل حفظ الحقل');
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Semantics(
          header: true,
          child: const Text('حذف الحقل'),
        ),
        content: const Text('هل أنت متأكد من حذف هذا الحقل؟ لا يمكن التراجع عن هذا الإجراء.'),
        actions: [
          Semantics(
            label: 'إلغاء الحذف',
            button: true,
            child: TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
          ),
          Semantics(
            label: 'تأكيد حذف الحقل',
            button: true,
            child: ElevatedButton(
              onPressed: () async {
                Navigator.pop(context); // Close dialog
                try {
                  final repo = ref.read(fieldsRepoProvider);
                  await repo.deleteField(widget.fieldId!);
                  if (!context.mounted) return;
                  AnnouncementHelper.announceComplete(context, 'حذف الحقل');
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('تم حذف الحقل بنجاح'),
                      backgroundColor: SahoolColors.forestGreen,
                    ),
                  );
                  Navigator.pop(context, 'deleted'); // Return to previous screen
                } catch (e) {
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('فشل حذف الحقل: $e'),
                      backgroundColor: SahoolColors.danger,
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.danger,
              ),
              child: const Text('حذف', style: TextStyle(color: Colors.white)),
            ),
          ),
        ],
      ),
    );
  }
}
