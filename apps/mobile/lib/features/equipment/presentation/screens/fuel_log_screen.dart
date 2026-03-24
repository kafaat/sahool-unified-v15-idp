/// Fuel Log Screen - شاشة سجل الوقود
/// Screen to add fuel log entries
library;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../state/equipment_providers.dart';
import '../widgets/fuel_gauge.dart';

/// Fuel Log Screen
class FuelLogScreen extends ConsumerStatefulWidget {
  final String equipmentId;

  const FuelLogScreen({
    super.key,
    required this.equipmentId,
  });

  @override
  ConsumerState<FuelLogScreen> createState() => _FuelLogScreenState();
}

class _FuelLogScreenState extends ConsumerState<FuelLogScreen> {
  final _formKey = GlobalKey<FormState>();
  final _quantityController = TextEditingController();
  final _priceController = TextEditingController();
  final _totalCostController = TextEditingController();
  final _odometerController = TextEditingController();
  final _stationController = TextEditingController();
  final _receiptController = TextEditingController();
  final _notesController = TextEditingController();

  FuelOperationType _operationType = FuelOperationType.refuel;
  double? _fuelLevelBefore;
  double? _fuelLevelAfter;
  bool _isSubmitting = false;
  bool _calculateFromPrice = true;

  @override
  void dispose() {
    _quantityController.dispose();
    _priceController.dispose();
    _totalCostController.dispose();
    _odometerController.dispose();
    _stationController.dispose();
    _receiptController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final equipmentAsync = ref.watch(equipmentDetailsProvider(widget.equipmentId));

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: const Text('تسجيل وقود'),
        backgroundColor: SahoolColors.forestGreen,
        foregroundColor: Colors.white,
      ),
      body: equipmentAsync.when(
        data: (equipment) => _buildForm(context, equipment),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text(error.toString())),
      ),
    );
  }

  Widget _buildForm(BuildContext context, Equipment equipment) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Current fuel level
            if (equipment.currentFuelPercent != null)
              Center(
                child: FuelGauge(
                  fuelPercent: equipment.currentFuelPercent!,
                  size: 120,
                  fuelLiters: equipment.currentFuelLiters,
                  capacity: equipment.fuelCapacityLiters,
                ),
              ),
            const SizedBox(height: 24),

            // Operation type
            const Text(
              'نوع العملية',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: FuelOperationType.values.take(3).map((type) {
                final isSelected = _operationType == type;
                return ChoiceChip(
                  label: Text(type.nameAr),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => _operationType = type);
                    }
                  },
                  selectedColor: SahoolColors.forestGreen.withValues(alpha: 0.2),
                  labelStyle: TextStyle(
                    color: isSelected ? SahoolColors.forestGreen : Colors.grey[700],
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // Quantity
            TextFormField(
              controller: _quantityController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'الكمية (لتر) *',
                hintText: 'مثال: 50',
                prefixIcon: const Icon(Icons.local_gas_station),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'الرجاء إدخال الكمية';
                }
                if (double.tryParse(value) == null) {
                  return 'الرجاء إدخال رقم صحيح';
                }
                return null;
              },
              onChanged: (_) => _calculateTotal(),
            ),
            const SizedBox(height: 16),

            // Price per liter
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _priceController,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(
                      labelText: 'سعر اللتر (ريال)',
                      hintText: 'مثال: 2.18',
                      prefixIcon: const Icon(Icons.attach_money),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (_) {
                      if (_calculateFromPrice) _calculateTotal();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _totalCostController,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(
                      labelText: 'إجمالي التكلفة',
                      hintText: 'تلقائي',
                      prefixIcon: const Icon(Icons.calculate),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (value) {
                      if (value.isNotEmpty) {
                        setState(() => _calculateFromPrice = false);
                      } else {
                        setState(() => _calculateFromPrice = true);
                        _calculateTotal();
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Odometer reading
            TextFormField(
              controller: _odometerController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'قراءة العداد (ساعات)',
                hintText: 'ساعات التشغيل الحالية',
                prefixIcon: const Icon(Icons.timer),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Fuel level before/after
            const Text(
              'مستوى الوقود',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('قبل', style: TextStyle(fontSize: 12)),
                      Slider(
                        value: _fuelLevelBefore ?? 0,
                        min: 0,
                        max: 100,
                        divisions: 20,
                        label: '${(_fuelLevelBefore ?? 0).toInt()}%',
                        activeColor: SahoolColors.forestGreen,
                        onChanged: (value) {
                          setState(() => _fuelLevelBefore = value);
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('بعد', style: TextStyle(fontSize: 12)),
                      Slider(
                        value: _fuelLevelAfter ?? 100,
                        min: 0,
                        max: 100,
                        divisions: 20,
                        label: '${(_fuelLevelAfter ?? 100).toInt()}%',
                        activeColor: SahoolColors.forestGreen,
                        onChanged: (value) {
                          setState(() => _fuelLevelAfter = value);
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Station name
            TextFormField(
              controller: _stationController,
              decoration: InputDecoration(
                labelText: 'اسم المحطة',
                hintText: 'مثال: محطة الراجحي',
                prefixIcon: const Icon(Icons.local_gas_station),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Receipt number
            TextFormField(
              controller: _receiptController,
              decoration: InputDecoration(
                labelText: 'رقم الفاتورة',
                hintText: 'اختياري',
                prefixIcon: const Icon(Icons.receipt),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Notes
            TextFormField(
              controller: _notesController,
              maxLines: 3,
              decoration: InputDecoration(
                labelText: 'ملاحظات',
                hintText: 'أي ملاحظات إضافية...',
                prefixIcon: const Icon(Icons.note),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 32),

            // Submit button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton.icon(
                onPressed: _isSubmitting ? null : _submitForm,
                icon: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.save),
                label: Text(_isSubmitting ? 'جاري الحفظ...' : 'حفظ'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  void _calculateTotal() {
    if (!_calculateFromPrice) return;

    final quantity = double.tryParse(_quantityController.text);
    final price = double.tryParse(_priceController.text);

    if (quantity != null && price != null) {
      final total = quantity * price;
      _totalCostController.text = total.toStringAsFixed(2);
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final controller = ref.read(equipmentControllerProvider.notifier);
      final success = await controller.addFuelLog(
        widget.equipmentId,
        operationType: _operationType,
        quantity: double.parse(_quantityController.text),
        pricePerLiter: double.tryParse(_priceController.text),
        totalCost: double.tryParse(_totalCostController.text),
        odometerReading: double.tryParse(_odometerController.text),
        fuelLevelBefore: _fuelLevelBefore,
        fuelLevelAfter: _fuelLevelAfter,
        stationName: _stationController.text.isNotEmpty
            ? _stationController.text
            : null,
        receiptNumber: _receiptController.text.isNotEmpty
            ? _receiptController.text
            : null,
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );

      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم تسجيل الوقود بنجاح'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('فشل في تسجيل الوقود'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
}
