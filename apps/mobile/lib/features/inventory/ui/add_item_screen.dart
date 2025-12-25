/// Add Item Screen - شاشة إضافة عنصر جديد
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../data/inventory_models.dart';
import '../providers/inventory_providers.dart';

/// شاشة إضافة عنصر مخزون جديد
class AddItemScreen extends ConsumerStatefulWidget {
  const AddItemScreen({super.key});

  @override
  ConsumerState<AddItemScreen> createState() => _AddItemScreenState();
}

class _AddItemScreenState extends ConsumerState<AddItemScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _nameArController = TextEditingController();
  final _skuController = TextEditingController();
  final _barcodeController = TextEditingController();
  final _reorderLevelController = TextEditingController();
  final _maxCapacityController = TextEditingController();
  final _unitPriceController = TextEditingController();
  final _batchNumberController = TextEditingController();
  final _lotNumberController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _descriptionArController = TextEditingController();

  ItemCategory _selectedCategory = ItemCategory.fertilizer;
  Unit _selectedUnit = Unit.kg;
  String? _selectedSupplierId;
  DateTime? _expiryDate;
  String? _imageUrl;

  @override
  void dispose() {
    _nameController.dispose();
    _nameArController.dispose();
    _skuController.dispose();
    _barcodeController.dispose();
    _reorderLevelController.dispose();
    _maxCapacityController.dispose();
    _unitPriceController.dispose();
    _batchNumberController.dispose();
    _lotNumberController.dispose();
    _descriptionController.dispose();
    _descriptionArController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;
    final suppliersAsync = ref.watch(suppliersProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('إضافة عنصر جديد'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // صورة العنصر
            Center(
              child: Stack(
                children: [
                  CircleAvatar(
                    radius: 60,
                    backgroundColor: Colors.grey.shade200,
                    child: _imageUrl != null
                        ? ClipOval(
                            child: Image.network(_imageUrl!, fit: BoxFit.cover),
                          )
                        : Icon(Icons.inventory_2, size: 60, color: Colors.grey.shade400),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: CircleAvatar(
                      backgroundColor: Theme.of(context).primaryColor,
                      child: IconButton(
                        icon: const Icon(Icons.camera_alt, color: Colors.white),
                        onPressed: _pickImage,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // الاسم (عربي)
            TextFormField(
              controller: _nameArController,
              decoration: const InputDecoration(
                labelText: 'الاسم (عربي) *',
                border: OutlineInputBorder(),
              ),
              validator: (value) =>
                  value == null || value.isEmpty ? 'الرجاء إدخال الاسم' : null,
            ),

            const SizedBox(height: 16),

            // الاسم (إنجليزي)
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Name (English) *',
                border: OutlineInputBorder(),
              ),
              validator: (value) =>
                  value == null || value.isEmpty ? 'Please enter name' : null,
            ),

            const SizedBox(height: 16),

            // الفئة والوحدة
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<ItemCategory>(
                    value: _selectedCategory,
                    decoration: const InputDecoration(
                      labelText: 'الفئة',
                      border: OutlineInputBorder(),
                    ),
                    items: ItemCategory.values.map((category) {
                      return DropdownMenuItem(
                        value: category,
                        child: Text(category.getName(locale)),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedCategory = value!;
                      });
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<Unit>(
                    value: _selectedUnit,
                    decoration: const InputDecoration(
                      labelText: 'الوحدة',
                      border: OutlineInputBorder(),
                    ),
                    items: Unit.values.map((unit) {
                      return DropdownMenuItem(
                        value: unit,
                        child: Text(unit.getName(locale)),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedUnit = value!;
                      });
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // SKU والباركود
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _skuController,
                    decoration: const InputDecoration(
                      labelText: 'SKU',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _barcodeController,
                    decoration: InputDecoration(
                      labelText: 'الباركود',
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.qr_code_scanner),
                        onPressed: _scanBarcode,
                      ),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // الحد الأدنى والحد الأقصى
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _reorderLevelController,
                    decoration: InputDecoration(
                      labelText: 'الحد الأدنى للطلب *',
                      border: const OutlineInputBorder(),
                      suffixText: _selectedUnit.getName(locale),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'مطلوب';
                      }
                      if (double.tryParse(value) == null) {
                        return 'رقم غير صحيح';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _maxCapacityController,
                    decoration: InputDecoration(
                      labelText: 'الحد الأقصى *',
                      border: const OutlineInputBorder(),
                      suffixText: _selectedUnit.getName(locale),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'مطلوب';
                      }
                      if (double.tryParse(value) == null) {
                        return 'رقم غير صحيح';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // المورد
            suppliersAsync.when(
              data: (suppliers) => DropdownButtonFormField<String>(
                value: _selectedSupplierId,
                decoration: const InputDecoration(
                  labelText: 'المورد (اختياري)',
                  border: OutlineInputBorder(),
                ),
                items: suppliers.map((supplier) {
                  return DropdownMenuItem(
                    value: supplier.supplierId,
                    child: Text(supplier.getDisplayName(locale)),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedSupplierId = value;
                  });
                },
              ),
              loading: () => const LinearProgressIndicator(),
              error: (_, __) => const SizedBox.shrink(),
            ),

            const SizedBox(height: 16),

            // السعر
            TextFormField(
              controller: _unitPriceController,
              decoration: const InputDecoration(
                labelText: 'السعر (ريال)',
                border: OutlineInputBorder(),
                prefixText: 'ريال ',
              ),
              keyboardType: TextInputType.number,
            ),

            const SizedBox(height: 16),

            // رقم الدفعة واللوت
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _batchNumberController,
                    decoration: const InputDecoration(
                      labelText: 'رقم الدفعة',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _lotNumberController,
                    decoration: const InputDecoration(
                      labelText: 'رقم اللوت',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // تاريخ الانتهاء
            ListTile(
              title: const Text('تاريخ الانتهاء'),
              subtitle: Text(
                _expiryDate != null
                    ? '${_expiryDate!.day}/${_expiryDate!.month}/${_expiryDate!.year}'
                    : 'غير محدد',
              ),
              trailing: const Icon(Icons.calendar_today),
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: DateTime.now().add(const Duration(days: 365)),
                  firstDate: DateTime.now(),
                  lastDate: DateTime.now().add(const Duration(days: 365 * 10)),
                );
                if (date != null) {
                  setState(() {
                    _expiryDate = date;
                  });
                }
              },
              tileColor: Colors.grey.shade50,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
                side: BorderSide(color: Colors.grey.shade300),
              ),
            ),

            const SizedBox(height: 16),

            // الوصف (عربي)
            TextFormField(
              controller: _descriptionArController,
              decoration: const InputDecoration(
                labelText: 'الوصف (عربي)',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 16),

            // الوصف (إنجليزي)
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (English)',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 24),

            // زر الحفظ
            ElevatedButton(
              onPressed: _submitForm,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: const Text('إضافة العنصر'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      // TODO: Upload image and get URL
      setState(() {
        _imageUrl = image.path;
      });
    }
  }

  Future<void> _scanBarcode() async {
    // TODO: Implement barcode scanning
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('الماسح الضوئي قيد التطوير')),
    );
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    final controller = ref.read(inventoryControllerProvider.notifier);
    final success = await controller.createItem(
      name: _nameController.text,
      nameAr: _nameArController.text,
      sku: _skuController.text.isEmpty ? null : _skuController.text,
      barcode: _barcodeController.text.isEmpty ? null : _barcodeController.text,
      category: _selectedCategory,
      unit: _selectedUnit,
      reorderLevel: double.parse(_reorderLevelController.text),
      maxCapacity: double.parse(_maxCapacityController.text),
      supplierId: _selectedSupplierId,
      unitPrice: _unitPriceController.text.isEmpty
          ? null
          : double.tryParse(_unitPriceController.text),
      batchNumber: _batchNumberController.text.isEmpty ? null : _batchNumberController.text,
      lotNumber: _lotNumberController.text.isEmpty ? null : _lotNumberController.text,
      expiryDate: _expiryDate,
      imageUrl: _imageUrl,
      description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
      descriptionAr:
          _descriptionArController.text.isEmpty ? null : _descriptionArController.text,
    );

    if (mounted) {
      if (success) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم إضافة العنصر بنجاح')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('فشل في إضافة العنصر')),
        );
      }
    }
  }
}
