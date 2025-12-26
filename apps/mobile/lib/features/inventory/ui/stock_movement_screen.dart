/// Stock Movement Screen - شاشة حركة المخزون
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/inventory_models.dart';
import '../providers/inventory_providers.dart';

/// شاشة تسجيل حركة المخزون
class StockMovementScreen extends ConsumerStatefulWidget {
  final InventoryItem item;
  final MovementType initialMovementType;

  const StockMovementScreen({
    super.key,
    required this.item,
    this.initialMovementType = MovementType.stockIn,
  });

  @override
  ConsumerState<StockMovementScreen> createState() => _StockMovementScreenState();
}

class _StockMovementScreenState extends ConsumerState<StockMovementScreen> {
  final _formKey = GlobalKey<FormState>();
  final _quantityController = TextEditingController();
  final _notesController = TextEditingController();
  final _notesArController = TextEditingController();
  final _referenceController = TextEditingController();

  late MovementType _selectedMovementType;
  String? _selectedFieldId;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _selectedMovementType = widget.initialMovementType;
  }

  @override
  void dispose() {
    _quantityController.dispose();
    _notesController.dispose();
    _notesArController.dispose();
    _referenceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;

    return Scaffold(
      appBar: AppBar(
        title: Text(_selectedMovementType.getName(locale)),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // معلومات العنصر
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.item.getDisplayName(locale),
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'المخزون الحالي: ${widget.item.currentStock.toStringAsFixed(1)} ${widget.item.unit.getName(locale)}',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // نوع الحركة
            DropdownButtonFormField<MovementType>(
              value: _selectedMovementType,
              decoration: const InputDecoration(
                labelText: 'نوع الحركة',
                border: OutlineInputBorder(),
              ),
              items: [
                MovementType.stockIn,
                MovementType.stockOut,
                MovementType.fieldApplication,
                MovementType.adjustment,
              ].map((type) {
                return DropdownMenuItem(
                  value: type,
                  child: Text(type.getName(locale)),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedMovementType = value!;
                });
              },
            ),

            const SizedBox(height: 16),

            // الكمية
            TextFormField(
              controller: _quantityController,
              decoration: InputDecoration(
                labelText: 'الكمية (${widget.item.unit.getName(locale)})',
                border: const OutlineInputBorder(),
                suffixText: widget.item.unit.getName(locale),
              ),
              keyboardType: TextInputType.number,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'الرجاء إدخال الكمية';
                }
                final quantity = double.tryParse(value);
                if (quantity == null || quantity <= 0) {
                  return 'الرجاء إدخال كمية صحيحة';
                }
                if (_selectedMovementType == MovementType.stockOut ||
                    _selectedMovementType == MovementType.fieldApplication) {
                  if (quantity > widget.item.currentStock) {
                    return 'الكمية أكبر من المخزون المتاح';
                  }
                }
                return null;
              },
            ),

            const SizedBox(height: 16),

            // محدد الحقل (للتطبيق الحقلي فقط)
            if (_selectedMovementType == MovementType.fieldApplication) ...[
              DropdownButtonFormField<String>(
                value: _selectedFieldId,
                decoration: const InputDecoration(
                  labelText: 'الحقل',
                  border: OutlineInputBorder(),
                ),
                items: const [], // TODO: Load fields from provider
                onChanged: (value) {
                  setState(() {
                    _selectedFieldId = value;
                  });
                },
                validator: (value) {
                  if (_selectedMovementType == MovementType.fieldApplication &&
                      (value == null || value.isEmpty)) {
                    return 'الرجاء اختيار الحقل';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
            ],

            // التاريخ
            ListTile(
              title: const Text('تاريخ الحركة'),
              subtitle: Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}'),
              trailing: const Icon(Icons.calendar_today),
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: _selectedDate,
                  firstDate: DateTime(2020),
                  lastDate: DateTime.now(),
                );
                if (date != null) {
                  setState(() {
                    _selectedDate = date;
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

            // المرجع
            TextFormField(
              controller: _referenceController,
              decoration: const InputDecoration(
                labelText: 'المرجع (اختياري)',
                hintText: 'رقم الفاتورة، الطلب، إلخ',
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 16),

            // الملاحظات (عربي)
            TextFormField(
              controller: _notesArController,
              decoration: const InputDecoration(
                labelText: 'الملاحظات (عربي)',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 16),

            // الملاحظات (إنجليزي)
            TextFormField(
              controller: _notesController,
              decoration: const InputDecoration(
                labelText: 'Notes (English) - Optional',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 24),

            // ملخص الحركة
            Card(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'ملخص الحركة',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 12),
                    _buildSummaryRow(
                      context,
                      'النوع',
                      _selectedMovementType.getName(locale),
                    ),
                    _buildSummaryRow(
                      context,
                      'الكمية',
                      _quantityController.text.isEmpty
                          ? '-'
                          : '${_quantityController.text} ${widget.item.unit.getName(locale)}',
                    ),
                    _buildSummaryRow(
                      context,
                      'المخزون الجديد',
                      _calculateNewStock(),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // زر الحفظ
            ElevatedButton(
              onPressed: _submitMovement,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: const Text('تأكيد الحركة'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }

  String _calculateNewStock() {
    final quantityText = _quantityController.text;
    if (quantityText.isEmpty) return '-';

    final quantity = double.tryParse(quantityText);
    if (quantity == null) return '-';

    double newStock = widget.item.currentStock;

    if (_selectedMovementType == MovementType.stockIn) {
      newStock += quantity;
    } else if (_selectedMovementType == MovementType.stockOut ||
        _selectedMovementType == MovementType.fieldApplication) {
      newStock -= quantity;
    }

    return '${newStock.toStringAsFixed(1)} ${widget.item.unit.getName(Localizations.localeOf(context).languageCode)}';
  }

  Future<void> _submitMovement() async {
    if (!_formKey.currentState!.validate()) return;

    final quantity = double.parse(_quantityController.text);
    final controller = ref.read(inventoryControllerProvider.notifier);
    bool success = false;

    switch (_selectedMovementType) {
      case MovementType.stockIn:
        success = await controller.stockIn(
          itemId: widget.item.itemId,
          quantity: quantity,
          reference: _referenceController.text.isEmpty ? null : _referenceController.text,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
          notesAr: _notesArController.text.isEmpty ? null : _notesArController.text,
          movementDate: _selectedDate,
        );
        break;
      case MovementType.stockOut:
        success = await controller.stockOut(
          itemId: widget.item.itemId,
          quantity: quantity,
          reference: _referenceController.text.isEmpty ? null : _referenceController.text,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
          notesAr: _notesArController.text.isEmpty ? null : _notesArController.text,
          movementDate: _selectedDate,
        );
        break;
      case MovementType.fieldApplication:
        if (_selectedFieldId != null) {
          success = await controller.applyToField(
            itemId: widget.item.itemId,
            quantity: quantity,
            fieldId: _selectedFieldId!,
            notes: _notesController.text.isEmpty ? null : _notesController.text,
            notesAr: _notesArController.text.isEmpty ? null : _notesArController.text,
            movementDate: _selectedDate,
          );
        }
        break;
      case MovementType.adjustment:
        success = await controller.adjustStock(
          itemId: widget.item.itemId,
          quantity: quantity,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
          notesAr: _notesArController.text.isEmpty ? null : _notesArController.text,
          movementDate: _selectedDate,
        );
        break;
      default:
        break;
    }

    if (mounted) {
      if (success) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم تسجيل الحركة بنجاح')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('فشل في تسجيل الحركة')),
        );
      }
    }
  }
}
