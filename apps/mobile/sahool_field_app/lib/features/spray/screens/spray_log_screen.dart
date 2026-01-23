/// Spray Log Screen - شاشة تسجيل الرش
/// نموذج لتسجيل تطبيق الرش
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import 'dart:io';

import '../models/spray_models.dart';
import '../providers/spray_provider.dart';

class SprayLogScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String? recommendationId;

  const SprayLogScreen({
    Key? key,
    required this.fieldId,
    this.recommendationId,
  }) : super(key: key);

  @override
  ConsumerState<SprayLogScreen> createState() => _SprayLogScreenState();
}

class _SprayLogScreenState extends ConsumerState<SprayLogScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form fields
  SprayType? _selectedSprayType;
  SprayProduct? _selectedProduct;
  final _appliedRateController = TextEditingController();
  final _areaController = TextEditingController();
  DateTime _applicationDate = DateTime.now();
  final _applicatorNameController = TextEditingController();
  final _equipmentController = TextEditingController();
  final _notesController = TextEditingController();
  final List<File> _photos = [];
  final List<String> _uploadedPhotoUrls = [];

  bool _isLoading = false;

  @override
  void dispose() {
    _appliedRateController.dispose();
    _areaController.dispose();
    _applicatorNameController.dispose();
    _equipmentController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final locale = Localizations.localeOf(context).languageCode;
    final isArabic = locale == 'ar';

    return Scaffold(
      appBar: AppBar(
        title: Text(isArabic ? 'تسجيل تطبيق الرش' : 'Log Spray Application'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Info Card
            Card(
              color: theme.colorScheme.primaryContainer,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        isArabic
                            ? 'سجل معلومات تطبيق الرش لتتبع استخدام المبيدات والأسمدة'
                            : 'Record spray application details to track pesticide and fertilizer usage',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onPrimaryContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Spray Type Selection
            Text(
              isArabic ? 'نوع الرش *' : 'Spray Type *',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            _buildSprayTypeSelector(theme, isArabic),
            const SizedBox(height: 24),

            // Product Selection
            Text(
              isArabic ? 'المنتج المستخدم *' : 'Product Used *',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            _buildProductSelector(theme, isArabic),
            const SizedBox(height: 24),

            // Application Details
            Text(
              isArabic ? 'تفاصيل التطبيق' : 'Application Details',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _appliedRateController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isArabic ? 'المعدل المطبق *' : 'Applied Rate *',
                      hintText: _selectedProduct != null
                          ? '${_selectedProduct!.recommendedRate}'
                          : '',
                      suffixText: _selectedProduct?.getUnit(_locale) ?? '',
                      border: const OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return isArabic ? 'مطلوب' : 'Required';
                      }
                      final rate = double.tryParse(value);
                      if (rate == null || rate <= 0) {
                        return isArabic ? 'قيمة غير صحيحة' : 'Invalid value';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _areaController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: isArabic ? 'المساحة (هكتار) *' : 'Area (ha) *',
                      border: const OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return isArabic ? 'مطلوب' : 'Required';
                      }
                      final area = double.tryParse(value);
                      if (area == null || area <= 0) {
                        return isArabic ? 'قيمة غير صحيحة' : 'Invalid value';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Application Date
            InkWell(
              onTap: () => _selectDate(context, isArabic),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: isArabic ? 'تاريخ التطبيق *' : 'Application Date *',
                  border: const OutlineInputBorder(),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      DateFormat('dd/MM/yyyy').format(_applicationDate),
                      style: theme.textTheme.bodyLarge,
                    ),
                    const Icon(Icons.calendar_today),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Additional Information
            Text(
              isArabic ? 'معلومات إضافية' : 'Additional Information',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _applicatorNameController,
              decoration: InputDecoration(
                labelText: isArabic ? 'اسم المطبق' : 'Applicator Name',
                hintText: isArabic ? 'من قام بتطبيق الرش؟' : 'Who applied the spray?',
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _equipmentController,
              decoration: InputDecoration(
                labelText: isArabic ? 'المعدة المستخدمة' : 'Equipment Used',
                hintText: isArabic ? 'مثال: رشاشة ظهرية' : 'e.g., Backpack Sprayer',
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _notesController,
              maxLines: 3,
              decoration: InputDecoration(
                labelText: isArabic ? 'ملاحظات' : 'Notes',
                hintText: isArabic
                    ? 'أي ملاحظات إضافية حول التطبيق'
                    : 'Any additional notes about the application',
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),

            // Photo Upload Section
            Text(
              isArabic ? 'الصور' : 'Photos',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildPhotoSection(theme, isArabic),
            const SizedBox(height: 24),

            // Weather Conditions (Read-only display)
            _buildCurrentWeatherCard(theme, isArabic),
            const SizedBox(height: 32),

            // Submit Button
            ElevatedButton(
              onPressed: _isLoading ? null : () => _submitForm(isArabic),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(
                      isArabic ? 'حفظ السجل' : 'Save Log',
                      style: const TextStyle(fontSize: 16),
                    ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildSprayTypeSelector(ThemeData theme, bool isArabic) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: SprayType.values.map((type) {
        final isSelected = _selectedSprayType == type;
        return FilterChip(
          selected: isSelected,
          label: Text(type.getName(_locale)),
          onSelected: (selected) {
            setState(() {
              _selectedSprayType = selected ? type : null;
              _selectedProduct = null; // Reset product when type changes
            });
          },
          backgroundColor: isSelected ? theme.colorScheme.primaryContainer : null,
          selectedColor: theme.colorScheme.primary,
          labelStyle: TextStyle(
            color: isSelected ? Colors.white : null,
          ),
        );
      }).toList(),
    );
  }

  Widget _buildProductSelector(ThemeData theme, bool isArabic) {
    if (_selectedSprayType == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            isArabic ? 'اختر نوع الرش أولاً' : 'Select spray type first',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ),
      );
    }

    final productsAsync = ref.watch(sprayProductsProvider(
      SprayProductFilter(sprayType: _selectedSprayType),
    ));

    return productsAsync.when(
      data: (products) {
        if (products.isEmpty) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                isArabic ? 'لا توجد منتجات متاحة' : 'No products available',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
            ),
          );
        }

        return DropdownButtonFormField<SprayProduct>(
          value: _selectedProduct,
          decoration: InputDecoration(
            labelText: isArabic ? 'اختر المنتج' : 'Select Product',
            border: const OutlineInputBorder(),
          ),
          items: products.map((product) {
            return DropdownMenuItem(
              value: product,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    product.getDisplayName(_locale),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    product.getActiveIngredient(_locale),
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
            );
          }).toList(),
          onChanged: (product) {
            setState(() {
              _selectedProduct = product;
              if (product != null) {
                _appliedRateController.text = product.recommendedRate.toString();
              }
            });
          },
          validator: (value) {
            if (value == null) {
              return isArabic ? 'مطلوب' : 'Required';
            }
            return null;
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            isArabic ? 'فشل في جلب المنتجات' : 'Failed to load products',
            style: TextStyle(color: theme.colorScheme.error),
          ),
        ),
      ),
    );
  }

  Widget _buildPhotoSection(ThemeData theme, bool isArabic) {
    return Column(
      children: [
        if (_photos.isNotEmpty) ...[
          SizedBox(
            height: 120,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _photos.length,
              itemBuilder: (context, index) {
                return Stack(
                  children: [
                    Container(
                      width: 120,
                      height: 120,
                      margin: const EdgeInsets.only(right: 8),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        image: DecorationImage(
                          image: FileImage(_photos[index]),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    Positioned(
                      top: 4,
                      right: 12,
                      child: IconButton(
                        icon: const Icon(Icons.close, color: Colors.white),
                        onPressed: () {
                          setState(() {
                            _photos.removeAt(index);
                          });
                        },
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.black54,
                          padding: const EdgeInsets.all(4),
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
          const SizedBox(height: 12),
        ],
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _pickImage(ImageSource.camera, isArabic),
                icon: const Icon(Icons.camera_alt),
                label: Text(isArabic ? 'التقاط صورة' : 'Take Photo'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _pickImage(ImageSource.gallery, isArabic),
                icon: const Icon(Icons.photo_library),
                label: Text(isArabic ? 'اختر من المعرض' : 'Choose from Gallery'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCurrentWeatherCard(ThemeData theme, bool isArabic) {
    final weatherAsync = ref.watch(currentWeatherProvider(widget.fieldId));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isArabic ? 'الظروف الجوية الحالية' : 'Current Weather Conditions',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        weatherAsync.when(
          data: (weather) => Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildWeatherItem(
                    Icons.thermostat,
                    '${weather.temperature.toStringAsFixed(0)}°C',
                    theme,
                  ),
                  _buildWeatherItem(
                    Icons.water_drop,
                    '${weather.humidity.toStringAsFixed(0)}%',
                    theme,
                  ),
                  _buildWeatherItem(
                    Icons.air,
                    '${weather.windSpeed.toStringAsFixed(0)} km/h',
                    theme,
                  ),
                  _buildWeatherItem(
                    Icons.umbrella,
                    '${weather.rainProbability.toStringAsFixed(0)}%',
                    theme,
                  ),
                ],
              ),
            ),
          ),
          loading: () => const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
          ),
          error: (error, stack) => const SizedBox.shrink(),
        ),
      ],
    );
  }

  Widget _buildWeatherItem(IconData icon, String value, ThemeData theme) {
    return Column(
      children: [
        Icon(icon, color: theme.colorScheme.primary),
        const SizedBox(height: 4),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Future<void> _selectDate(BuildContext context, bool isArabic) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _applicationDate,
      firstDate: DateTime.now().subtract(const Duration(days: 30)),
      lastDate: DateTime.now(),
      locale: Locale(isArabic ? 'ar' : 'en'),
    );

    if (picked != null) {
      setState(() {
        _applicationDate = picked;
      });
    }
  }

  Future<void> _pickImage(ImageSource source, bool isArabic) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);

    if (pickedFile != null) {
      setState(() {
        _photos.add(File(pickedFile.path));
      });
    }
  }

  Future<void> _submitForm(bool isArabic) async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_selectedSprayType == null || _selectedProduct == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isArabic ? 'يرجى اختيار نوع الرش والمنتج' : 'Please select spray type and product',
          ),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final controller = ref.read(sprayControllerProvider.notifier);

      // Upload photos first
      for (final photo in _photos) {
        final photoUrl = await controller.uploadPhoto(photo.path);
        if (photoUrl != null) {
          _uploadedPhotoUrls.add(photoUrl);
        }
      }

      // Submit spray log
      final log = await controller.logSprayApplication(
        fieldId: widget.fieldId,
        recommendationId: widget.recommendationId,
        sprayType: _selectedSprayType!,
        productId: _selectedProduct!.productId,
        appliedRate: double.parse(_appliedRateController.text),
        unit: _selectedProduct!.unit,
        unitAr: _selectedProduct!.unitAr,
        area: double.parse(_areaController.text),
        applicationDate: _applicationDate,
        applicatorName: _applicatorNameController.text.isEmpty
            ? null
            : _applicatorNameController.text,
        equipmentUsed: _equipmentController.text.isEmpty ? null : _equipmentController.text,
        photoUrls: _uploadedPhotoUrls,
        notes: _notesController.text.isEmpty ? null : _notesController.text,
        notesAr: _notesController.text.isEmpty ? null : _notesController.text,
      );

      if (log != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                isArabic ? 'تم حفظ السجل بنجاح' : 'Log saved successfully',
              ),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.of(context).pop(log);
        }
      } else {
        throw Exception(isArabic ? 'فشل في حفظ السجل' : 'Failed to save log');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString()),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}
