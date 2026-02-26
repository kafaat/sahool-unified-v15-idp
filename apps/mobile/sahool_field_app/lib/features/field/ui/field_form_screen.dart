import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/config/env_config.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../../../core/http/api_client.dart';
import '../../../core/utils/app_logger.dart';
import '../../crops/data/models/crop_model.dart';
import '../../crops/data/remote/crops_api.dart';
import '../../crops/data/repositories/crops_repository.dart';
import '../../polygon_editor/utils/geo_utils.dart';
import '../presentation/providers/field_controller.dart';

/// شاشة إضافة/تعديل الحقل - Smart Form
/// نموذج بسيط وسهل الاستخدام لإدخال بيانات الحقل
class FieldFormScreen extends ConsumerStatefulWidget {
  final String? fieldId; // null = إضافة جديد
  final String? tenantId; // Tenant ID for creating fields
  final List<LatLng>? initialBoundary; // Initial boundary from map drawing

  const FieldFormScreen({
    super.key,
    this.fieldId,
    this.tenantId,
    this.initialBoundary,
  });

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
  List<LatLng> _boundary = [];
  double _calculatedArea = 0;

  // Saving state
  bool _isSaving = false;

  // Crops data
  List<Crop> _crops = [];
  bool _isLoadingCrops = true;
  String? _cropsError;
  late CropsRepository _cropsRepository;

  bool get isEditing => widget.fieldId != null;
  String get _tenantId => widget.tenantId ?? EnvConfig.defaultTenantId;

  @override
  void initState() {
    super.initState();
    _initializeCropsRepository();

    // Initialize boundary from passed data
    if (widget.initialBoundary != null && widget.initialBoundary!.isNotEmpty) {
      _boundary = List.from(widget.initialBoundary!);
      _hasBoundary = true;
      _calculatedArea = GeoUtils.calculateAreaHectares(_boundary);
      _areaController.text = _calculatedArea.toStringAsFixed(2);
    }

    // Load existing field data if editing
    if (isEditing) {
      _loadExistingField();
    }
  }

  Future<void> _loadExistingField() async {
    // Load field data from repository for editing
    try {
      final controller = ref.read(fieldControllerProvider(_tenantId).notifier);
      final field = controller.getFieldById(widget.fieldId!);
      if (field != null) {
        setState(() {
          _nameController.text = field.name;
          _selectedCrop = field.cropType;
          if (field.hasBoundary) {
            _boundary = field.boundary;
            _hasBoundary = true;
            _calculatedArea = field.areaHectares;
            _areaController.text = _calculatedArea.toStringAsFixed(2);
          }
        });
      }
    } catch (e) {
      AppLogger.e('Failed to load field for editing', error: e);
    }
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
        title: Text(isEditing ? "تعديل الحقل" : "إضافة حقل جديد"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          if (isEditing)
            IconButton(
              icon:
                  const Icon(Icons.delete_outline, color: SahoolColors.danger),
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
              _buildCropDropdown(),
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
                  DropdownMenuItem(
                      value: "none", child: Text("بدون ري (مطري)")),
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
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation(Colors.white),
                        ),
                      )
                    : Text(
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

  Widget _buildCropDropdown() {
    if (_isLoadingCrops) {
      return InputDecorator(
        decoration: const InputDecoration(
          labelText: "نوع المحصول",
          prefixIcon: Icon(Icons.grass),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 8),
            Text("جاري التحميل...", style: TextStyle(fontSize: 12)),
          ],
        ),
      );
    }

    if (_cropsError != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          InputDecorator(
            decoration: const InputDecoration(
              labelText: "نوع المحصول",
              prefixIcon: Icon(Icons.grass),
            ),
            child: Text(
              _cropsError!,
              style: const TextStyle(color: Colors.red, fontSize: 12),
            ),
          ),
          const SizedBox(height: 8),
          TextButton.icon(
            onPressed: _loadCrops,
            icon: const Icon(Icons.refresh),
            label: const Text("إعادة المحاولة"),
          ),
        ],
      );
    }

    if (_crops.isEmpty) {
      return InputDecorator(
        decoration: const InputDecoration(
          labelText: "نوع المحصول",
          prefixIcon: Icon(Icons.grass),
        ),
        child: const Text(
          "لا توجد محاصيل متاحة",
          style: TextStyle(color: Colors.grey, fontSize: 12),
        ),
      );
    }

    return DropdownButtonFormField<String>(
      value: _selectedCrop,
      decoration: InputDecoration(
        labelText: "نوع المحصول",
        prefixIcon: const Icon(Icons.grass),
        suffixIcon: _crops.length > 10
            ? IconButton(
                icon: const Icon(Icons.search, size: 20),
                onPressed: _showCropSearchDialog,
                tooltip: "البحث عن محصول",
              )
            : null,
      ),
      items: _crops.map((crop) {
        return DropdownMenuItem<String>(
          value: crop.code,
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
            title: const Text("اختر المحصول"),
            content: SizedBox(
              width: double.maxFinite,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    decoration: const InputDecoration(
                      labelText: "البحث",
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
                child: const Text("إلغاء"),
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
    return OrganicCard(
      color: _hasBoundary
          ? SahoolColors.sageGreen.withOpacity(0.1)
          : SahoolColors.paleOlive.withOpacity(0.5),
      child: Column(
        children: [
          Icon(
            _hasBoundary ? Icons.check_circle : Icons.map_outlined,
            size: 48,
            color: _hasBoundary
                ? SahoolColors.sageGreen
                : SahoolColors.forestGreen,
          ),
          const SizedBox(height: 12),
          Text(
            _hasBoundary ? "تم تحديد الحدود" : "لم يتم تحديد الحدود",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: _hasBoundary
                  ? SahoolColors.sageGreen
                  : SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(height: 8),
          if (_hasBoundary)
            Text(
              "المساحة: ${_calculatedArea.toStringAsFixed(2)} هكتار",
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
          if (_hasBoundary)
            Text(
              "${_boundary.length} نقاط",
              style: const TextStyle(color: Colors.grey, fontSize: 11),
            ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () async {
              final result = await context.push<Map<String, dynamic>>(
                '/map',
                extra: {
                  'mode': 'draw',
                  'tenantId': _tenantId,
                  'existingBoundary': _boundary.isNotEmpty ? _boundary : null,
                },
              );

              if (result != null && result['boundary'] != null) {
                final newBoundary = result['boundary'] as List<LatLng>;
                if (newBoundary.length >= 3) {
                  setState(() {
                    _boundary = newBoundary;
                    _hasBoundary = true;
                    _calculatedArea = GeoUtils.calculateAreaHectares(_boundary);
                    _areaController.text = _calculatedArea.toStringAsFixed(2);
                  });
                }
              }
            },
            icon: Icon(_hasBoundary ? Icons.edit : Icons.draw),
            label:
                Text(_hasBoundary ? "تعديل الحدود" : "رسم الحدود على الخريطة"),
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

  Future<void> _saveField() async {
    if (!_formKey.currentState!.validate()) return;

    // Validate boundary
    if (!_hasBoundary || _boundary.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('الرجاء رسم حدود الحقل على الخريطة'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isSaving = true);

    try {
      final controller = ref.read(fieldControllerProvider(_tenantId).notifier);

      if (isEditing) {
        // Update existing field
        final success = await controller.updateFieldProperties(
          fieldId: widget.fieldId!,
          name: _nameController.text.trim(),
          cropType: _selectedCrop,
        );

        if (!mounted) return;

        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم تحديث الحقل بنجاح'),
              backgroundColor: SahoolColors.forestGreen,
            ),
          );
          Navigator.pop(context, true);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('فشل تحديث الحقل'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } else {
        // Create new field
        final field = await controller.createField(
          name: _nameController.text.trim(),
          boundary: _boundary,
          cropType: _selectedCrop,
        );

        if (!mounted) return;

        if (field != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('تم إضافة الحقل "${field.name}" بنجاح'),
              backgroundColor: SahoolColors.forestGreen,
            ),
          );
          Navigator.pop(context, true);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('فشل إضافة الحقل'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      AppLogger.e('Failed to save field', error: e);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text("حذف الحقل"),
        content: const Text(
            "هل أنت متأكد من حذف هذا الحقل؟ لا يمكن التراجع عن هذا الإجراء."),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text("إلغاء"),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(dialogContext);
              await _deleteField();
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

  Future<void> _deleteField() async {
    if (widget.fieldId == null) return;

    setState(() => _isSaving = true);

    try {
      final controller = ref.read(fieldControllerProvider(_tenantId).notifier);
      final success = await controller.deleteField(widget.fieldId!);

      if (!mounted) return;

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم حذف الحقل بنجاح'),
            backgroundColor: SahoolColors.forestGreen,
          ),
        );
        Navigator.pop(context, 'deleted');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('فشل حذف الحقل'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      AppLogger.e('Failed to delete field', error: e);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }
}
