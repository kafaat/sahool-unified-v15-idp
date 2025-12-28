/// GDD Settings Screen - شاشة إعدادات درجات النمو الحراري
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/gdd_models.dart';
import '../providers/gdd_provider.dart';

/// شاشة إعدادات GDD
class GDDSettingsScreen extends ConsumerStatefulWidget {
  final String fieldId;

  const GDDSettingsScreen({
    super.key,
    required this.fieldId,
  });

  @override
  ConsumerState<GDDSettingsScreen> createState() => _GDDSettingsScreenState();
}

class _GDDSettingsScreenState extends ConsumerState<GDDSettingsScreen> {
  final _formKey = GlobalKey<FormState>();

  CropType _selectedCrop = CropType.wheat;
  double _baseTemperature = 10.0;
  double _upperThreshold = 30.0;
  GDDCalculationMethod _calculationMethod = GDDCalculationMethod.average;
  DateTime _plantingDate = DateTime.now();
  DateTime? _harvestDate;
  bool _autoCalculate = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final settingsAsync = ref.read(gddSettingsProvider(widget.fieldId));
    await settingsAsync.whenOrNull(
      data: (settings) {
        if (settings != null) {
          setState(() {
            _selectedCrop = settings.cropType;
            _baseTemperature = settings.baseTemperature;
            _upperThreshold = settings.upperThreshold;
            _calculationMethod = settings.calculationMethod;
            _plantingDate = settings.plantingDate;
            _harvestDate = settings.harvestDate;
            _autoCalculate = settings.autoCalculate;
          });
        }
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final settingsAsync = ref.watch(gddSettingsProvider(widget.fieldId));
    final controllerState = ref.watch(gddSettingsControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('إعدادات GDD'),
        actions: [
          // حفظ الإعدادات
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _isLoading ? null : _saveSettings,
          ),
        ],
      ),
      body: settingsAsync.when(
        data: (settings) => _buildForm(context, settings),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => _buildForm(context, null),
      ),
    );
  }

  Widget _buildForm(BuildContext context, GDDSettings? existingSettings) {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // معلومات
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(Icons.info, color: Colors.blue.shade700),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'قم بتكوين إعدادات GDD لحساب درجات النمو الحراري بدقة',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // اختيار المحصول
          Text(
            'نوع المحصول',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Card(
            child: DropdownButtonFormField<CropType>(
              value: _selectedCrop,
              decoration: const InputDecoration(
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                prefixIcon: Icon(Icons.grass),
              ),
              items: CropType.values.map((crop) {
                return DropdownMenuItem(
                  value: crop,
                  child: Text(crop.getName('ar')),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedCrop = value;
                  });
                  _loadCropDefaults(value);
                }
              },
            ),
          ),
          const SizedBox(height: 24),

          // درجة الأساس
          Text(
            'درجة الحرارة الأساسية (°C)',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'درجة الأساس: ${_baseTemperature.toStringAsFixed(1)}°C',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: _baseTemperature,
                    min: 0,
                    max: 20,
                    divisions: 40,
                    label: _baseTemperature.toStringAsFixed(1),
                    onChanged: (value) {
                      setState(() {
                        _baseTemperature = value;
                      });
                    },
                  ),
                  Text(
                    'درجة الحرارة الأساسية التي يبدأ عندها نمو المحصول',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // الحد الأعلى
          Text(
            'الحد الأعلى لدرجة الحرارة (°C)',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'الحد الأعلى: ${_upperThreshold.toStringAsFixed(1)}°C',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: _upperThreshold,
                    min: 25,
                    max: 40,
                    divisions: 30,
                    label: _upperThreshold.toStringAsFixed(1),
                    onChanged: (value) {
                      setState(() {
                        _upperThreshold = value;
                      });
                    },
                  ),
                  Text(
                    'درجة الحرارة القصوى التي يتوقف عندها النمو الإضافي',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // طريقة الحساب
          Text(
            'طريقة الحساب',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          ...GDDCalculationMethod.values.map((method) {
            return Card(
              child: RadioListTile<GDDCalculationMethod>(
                title: Text(method.getName('ar')),
                subtitle: Text(_getMethodDescription(method)),
                value: method,
                groupValue: _calculationMethod,
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _calculationMethod = value;
                    });
                  }
                },
              ),
            );
          }).toList(),
          const SizedBox(height: 24),

          // تاريخ الزراعة
          Text(
            'تاريخ الزراعة',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Card(
            child: ListTile(
              leading: const Icon(Icons.event),
              title: Text(DateFormat('dd MMMM yyyy', Localizations.localeOf(context).languageCode).format(_plantingDate)),
              subtitle: const Text('اضغط للتغيير'),
              onTap: () => _selectPlantingDate(context),
            ),
          ),
          const SizedBox(height: 24),

          // تاريخ الحصاد (اختياري)
          Text(
            'تاريخ الحصاد المتوقع (اختياري)',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Card(
            child: ListTile(
              leading: const Icon(Icons.event_available),
              title: Text(
                _harvestDate != null
                    ? DateFormat('dd MMMM yyyy', Localizations.localeOf(context).languageCode).format(_harvestDate!)
                    : 'غير محدد',
              ),
              subtitle: const Text('اضغط للتغيير'),
              trailing: _harvestDate != null
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        setState(() {
                          _harvestDate = null;
                        });
                      },
                    )
                  : null,
              onTap: () => _selectHarvestDate(context),
            ),
          ),
          const SizedBox(height: 24),

          // الحساب التلقائي
          Card(
            child: SwitchListTile(
              title: const Text('الحساب التلقائي'),
              subtitle: const Text('حساب GDD تلقائياً من بيانات الطقس'),
              value: _autoCalculate,
              onChanged: (value) {
                setState(() {
                  _autoCalculate = value;
                });
              },
            ),
          ),
          const SizedBox(height: 32),

          // أزرار الحفظ والإلغاء
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _isLoading ? null : () => Navigator.pop(context),
                  child: const Text('إلغاء'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _saveSettings,
                  child: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('حفظ'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  String _getMethodDescription(GDDCalculationMethod method) {
    switch (method) {
      case GDDCalculationMethod.average:
        return 'طريقة المتوسط البسيط - الأكثر استخداماً';
      case GDDCalculationMethod.sine:
        return 'طريقة الموجة الجيبية - دقة أعلى';
      case GDDCalculationMethod.modifiedAverage:
        return 'طريقة المتوسط المعدل - مع تعديل للحدود';
    }
  }

  Future<void> _selectPlantingDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _plantingDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now().add(const Duration(days: 30)),
      locale: const Locale('ar'),
    );

    if (picked != null) {
      setState(() {
        _plantingDate = picked;
      });
    }
  }

  Future<void> _selectHarvestDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _harvestDate ?? _plantingDate.add(const Duration(days: 120)),
      firstDate: _plantingDate,
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: const Locale('ar'),
    );

    if (picked != null) {
      setState(() {
        _harvestDate = picked;
      });
    }
  }

  Future<void> _loadCropDefaults(CropType cropType) async {
    final requirementsAsync = ref.read(cropGDDRequirementsProvider(cropType));
    await requirementsAsync.whenOrNull(
      data: (requirements) {
        if (requirements != null) {
          setState(() {
            _baseTemperature = requirements.baseTemperature;
            _upperThreshold = requirements.upperThreshold;
          });
        }
      },
    );
  }

  Future<void> _saveSettings() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final settings = GDDSettings(
      fieldId: widget.fieldId,
      cropType: _selectedCrop,
      baseTemperature: _baseTemperature,
      upperThreshold: _upperThreshold,
      calculationMethod: _calculationMethod,
      plantingDate: _plantingDate,
      harvestDate: _harvestDate,
      autoCalculate: _autoCalculate,
    );

    final controller = ref.read(gddSettingsControllerProvider.notifier);

    // تحقق مما إذا كانت الإعدادات موجودة
    final existingSettings = await ref.read(gddSettingsProvider(widget.fieldId).future);

    final success = existingSettings != null
        ? await controller.updateSettings(widget.fieldId, settings)
        : await controller.createSettings(settings);

    setState(() {
      _isLoading = false;
    });

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('تم حفظ الإعدادات بنجاح'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('فشل في حفظ الإعدادات'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
